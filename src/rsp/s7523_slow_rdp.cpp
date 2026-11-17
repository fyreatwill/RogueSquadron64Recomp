// s7523 class FT: finite-rate RDP model for the RSP-side DPC registers.
// ROGUESQ_S7523_SLOWRDP=<bytes_per_poll>[,<bytes_per_task_gap>] (default off).
// s7095 closed the DPC register model against an INSTANT RDP. Hardware's RDP drains [CURRENT, END) at a finite rate,
// so a task can start while the previous task's list is still draining (CURRENT != END), which the port never shows:
// the ucode's task-entry resume path (L_1DB0 branch 5, j L_1E5C) and the ring wait loops (L_114C / L_115C / L_116C,
// L_1E48) are then live. In this mode every DPC read (CURRENT, END, STATUS) comes from a queue model of the RDP
// instead of the bridge's instant values, and the model RDP consumes <rate> bytes per DPC read (a poll costs time)
// plus <gap> bytes between tasks. Nothing else changes: the bridge still forwards each END write to RT64 at once.
// Measured:
//   - entry: tasks whose first DPC read saw a busy RDP (CURRENT != END), i.e. path A is reachable,
//   - polls while busy, longest busy spin, START_VALID-pending reads, deadlock escapes (4096 polls without progress),
//   - OVERWRITE: bytes the model RDP consumes that differ from the bytes RT64 got at the END write (= what a hardware RDP
//     would draw differently from the port because the ring was rewritten before it was consumed). Ctl: every 997th
//     queued range has one snapshot byte flipped; each must be caught (ctl_planted == ctl_caught).
// s7524 writer attribution (same env): RSP DMEM->RDRAM DMA writes (s7094 hook) mark every queued not-yet-consumed byte they
// overwrite (tch: 1 gfx, 2 audio ucode); at consume each mismatch byte is attributed rsp_gfx / rsp_aud / resid. Every 256th END
// the whole queue is scanned before and after rsp_dpc_submit: new untouched mismatches inside submit = bridge. Ctl: DMA coverage of
// pushed bytes (every pushed ring byte must have been written by an RSP DMA since its last push: cov ~ 1.0).
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <deque>
#include <vector>
#include <mutex>

extern "C" int rs64_s7523_on = 0;
extern "C" uint32_t rs64_dpc_get_cumulative_fullsyncs();   // dpc_bridge.cpp: FULL_SYNCs forwarded (= DP interrupts the CPU sees)
namespace {
uint32_t g_rate = 8, g_gap = 0;
struct R { uint32_t lo, hi; size_t off; bool ctl, st; uint64_t task; };   // st: begins a new list (bound START)   // pending range, snapshot at off
std::deque<R> q;              // q.front() is draining; cur = q.front().lo
std::vector<uint8_t> snap;    // ring of snapshot bytes (offset base advances on pop)
std::vector<uint8_t> tch;     // s7524: parallel to snap; 1 = overwritten by a gfx RSP DMA after push, 2 = audio-ucode DMA
struct S { uint32_t lo, hi; size_t off; };   // s7524: contiguous merge of q (same bytes, same order)
std::deque<S> sg;
std::vector<uint8_t> dmabit(1u << 21);   // s7524 ctl: 16 MB bit map of bytes written by a gfx RSP DMA since their last push
uint64_t cov_b = 0, push_b = 0, ov_dma[2] = {}, ov_dmab[2] = {}, att[3] = {}, ov_told[2] = {}, dma_w[2] = {}, ahead_w = 0;
uint64_t dma_hi = 0, br_pairs = 0, br_hit = 0, br_bytes = 0, br_skip = 0, pre_bad = 0; bool pre_on = false; uint32_t last_ret = 0; uint64_t reads_since_end = 0;
char dex[16][220]; int ndex = 0; char rex[8][160]; int nrex = 0;
size_t snap_base = 0;
uint32_t m_end = 0, m_start = 0; bool m_sv = false;   // last END written; START written, not yet bound by an END
const uint8_t* g_rd = nullptr;
uint64_t tasks = 0, entry_busy = 0, entry_seen = 0, reads = 0, busy_reads = 0, sv_reads = 0, escapes = 0;
uint64_t spin = 0, max_spin = 0, consumed = 0, over_bytes = 0, over_ranges = 0, ranges = 0, ctl_planted = 0, ctl_caught = 0;
uint64_t over_age[3] = {}, over_age_b[3] = {}; char ex[16][200]; int nex = 0; uint64_t op_b[2][64] = {};   // mismatch consumed in the push task / the next task / later
bool first_read_of_task = false; uint64_t st_pending = 0, skipped = 0, same = 0; uint32_t last_c = 0xFFFFFFFFu;
time_t g_last = 0;
uint32_t fs_seen = 0; uint64_t fs_drains = 0, fs_drained = 0;
// Hardware raises DP only once the RDP has consumed FULL_SYNC, so the CPU cannot reuse a buffer before that; the port raises
// it at forward time. Drain the model at each forwarded FULL_SYNC so it never lags past the CPU's completion signal.
void consume(uint32_t n);
void fs_gate() { uint32_t c = rs64_dpc_get_cumulative_fullsyncs(); if (c != fs_seen) { fs_seen = c; ++fs_drains; uint64_t b = consumed; consume(0xFFFFFF); fs_drained += consumed - b; } }
std::mutex g_mu;   // ucode B (RSP task thread) and the gfx ucode (gfx thread) both read DPC_STATUS
uint64_t b_reads = 0;
inline bool busy() { return !q.empty(); }
inline uint32_t cur() { return q.empty() ? m_end : q.front().lo; }
void consume(uint32_t n) {
    while (n && !q.empty()) {
        R& h = q.front();
        uint32_t take = h.hi - h.lo; if (take > n) take = n;
        // compare what the model RDP reads now with what RT64 got at the END write
        if (g_rd) {
            const uint8_t* s = &snap[h.off - snap_base];
            uint32_t bad = 0;
            for (uint32_t i = 0; i < take; i++) if (g_rd[(h.lo + i) ^ 3] != s[i]) bad++;
            if (bad && !h.ctl) { const uint8_t* t = &tch[h.off - snap_base]; for (uint32_t i = 0; i < take; i++) if (g_rd[(h.lo + i) ^ 3] != s[i]) { int k = t[i] == 1 ? 0 : t[i] == 2 ? 1 : 2; att[k]++;
                  if (k == 2 && nrex < 8) snprintf(rex[nrex++], sizeof rex[0], "task=%llu push=%llu a=0x%06X snap=%02X now=%02X", (unsigned long long)tasks, (unsigned long long)h.task, h.lo + i, s[i], g_rd[(h.lo + i) ^ 3]); } }
            if (bad) {
                if (h.ctl) { ctl_caught++; h.ctl = false; }
                else { over_bytes += bad; over_ranges++; { uint64_t a = tasks - h.task; int k = a == 0 ? 0 : a == 1 ? 1 : 2; over_age[k]++; over_age_b[k] += bad; } { int k2 = (tasks == h.task) ? 0 : 1; for (uint32_t i = 0; i < take; i++) if (g_rd[(h.lo + i) ^ 3] != s[i]) { uint32_t a = (h.lo + i) & ~7u; uint32_t si = a >= h.lo ? 0 : 0; (void)si; op_b[k2][g_rd[a ^ 3] & 0x3F]++; } }
                  if (nex < 16) { char hx[2][20]; for (int w = 0; w < 2; w++) for (uint32_t i = 0; i < 8 && i < take; i++) snprintf(hx[w] + 2 * i, 3, "%02X", w ? g_rd[(h.lo + i) ^ 3] : s[i]); hx[0][2*(take<8?take:8)] = hx[1][2*(take<8?take:8)] = 0;
                    snprintf(ex[nex++], sizeof ex[0], "task=%llu push=%llu lo=0x%06X take=%u bad=%u snap=%s now=%s", (unsigned long long)tasks, (unsigned long long)h.task, h.lo, take, bad, hx[0], hx[1]); } }
            }
        }
        h.lo += take; h.off += take; n -= take; consumed += take;
        for (uint32_t t2 = take; t2 && !sg.empty();) { S& f = sg.front(); uint32_t u = f.hi - f.lo; if (u > t2) u = t2; f.lo += u; f.off += u; t2 -= u; if (f.lo == f.hi) sg.pop_front(); }
        if (h.lo == h.hi) {
            if (h.ctl) h.ctl = false;   // a planted flip in a range never compared would be a ctl miss (counted below)
            q.pop_front();
            if (!q.empty() && q.front().st) --st_pending;
            if (q.empty()) { snap.clear(); tch.clear(); sg.clear(); snap_base = 0; }
            else if (q.front().off - snap_base > (1u << 20)) { size_t d = q.front().off - snap_base; snap.erase(snap.begin(), snap.begin() + d); tch.erase(tch.begin(), tch.begin() + d); snap_base += d; }
        }
    }
}
void push(uint32_t lo, uint32_t hi, bool st) {
    if (hi < lo || hi - lo > 0x100000u || !g_rd) { ++skipped; return; }
    if (hi == lo && !st) return;
    if (q.empty()) { snap.clear(); tch.clear(); sg.clear(); snap_base = 0; }
    R r{lo, hi, snap_base + snap.size(), false, st, tasks};
    if (st && !q.empty()) ++st_pending;
    for (uint32_t a = lo; a < hi; a++) { snap.push_back(g_rd[a ^ 3]); tch.push_back(0); uint8_t& m = dmabit[a >> 3]; if (m & (1u << (a & 7))) { ++cov_b; m &= ~(1u << (a & 7)); } }
    push_b += hi - lo;
    if (hi > lo) { if (!sg.empty() && sg.back().hi == lo && sg.back().off + (sg.back().hi - sg.back().lo) == r.off) sg.back().hi = hi; else sg.push_back({lo, hi, r.off}); }
    if (hi > lo && ++ranges % 997 == 0) { snap[r.off - snap_base] ^= 0x5A; r.ctl = true; ctl_planted++; }
    q.push_back(r);
}
uint64_t scan_bad() {   // untouched, non-ctl mismatching queued bytes
    uint64_t b = 0; if (!g_rd) return 0;
    for (const R& h : q) { if (h.ctl) continue; const uint8_t* sp = &snap[h.off - snap_base]; const uint8_t* t = &tch[h.off - snap_base];
        for (uint32_t i = 0; i < h.hi - h.lo; i++) if (!t[i] && g_rd[(h.lo + i) ^ 3] != sp[i]) b++; }
    return b;
}
void dump(const char* why) {
    std::fprintf(stderr, "[s7523-fs] drains=%llu drained=%llu\n", (unsigned long long)fs_drains, (unsigned long long)fs_drained);
    std::fprintf(stderr, "[s7523-sum] why=%s rate=%u gap=%u tasks=%llu entry_seen=%llu entry_busy=%llu reads=%llu busy_reads=%llu sv_reads=%llu "
                 "max_spin=%llu escapes=%llu ranges=%llu consumed=%llu over_ranges=%llu over_bytes=%llu ctl_planted=%llu ctl_caught=%llu skipped=%llu qlen=%zu over_same=%llu/%llu over_next=%llu/%llu over_later=%llu/%llu\n",
                 why, g_rate, g_gap, (unsigned long long)tasks, (unsigned long long)entry_seen, (unsigned long long)entry_busy,
                 (unsigned long long)reads, (unsigned long long)busy_reads, (unsigned long long)sv_reads, (unsigned long long)max_spin,
                 (unsigned long long)escapes, (unsigned long long)ranges, (unsigned long long)consumed, (unsigned long long)over_ranges,
                 (unsigned long long)over_bytes, (unsigned long long)ctl_planted, (unsigned long long)ctl_caught, (unsigned long long)skipped, q.size(), (unsigned long long)over_age[0], (unsigned long long)over_age_b[0], (unsigned long long)over_age[1], (unsigned long long)over_age_b[1], (unsigned long long)over_age[2], (unsigned long long)over_age_b[2]);
    for (int i = 0; i < nex; i++) std::fprintf(stderr, "[s7523-ex] %s\n", ex[i]);
    std::fprintf(stderr, "[s7524-sum] why=%s push_b=%llu cov_b=%llu cov=%.4f dma_w_gfx=%llu dma_w_aud=%llu ahead_w=%llu ov_dma_gfx=%llu/%llu ov_dma_aud=%llu/%llu ov_told_busy=%llu ov_not_told=%llu "
                 "att_rsp_gfx=%llu att_rsp_aud=%llu att_resid=%llu br_pairs=%llu br_hit=%llu br_bytes=%llu br_skip=%llu segs=%zu dma_gfx_hi8=%llu\n", why,
                 (unsigned long long)push_b, (unsigned long long)cov_b, push_b ? (double)cov_b / push_b : 0.0, (unsigned long long)dma_w[0], (unsigned long long)dma_w[1], (unsigned long long)ahead_w,
                 (unsigned long long)ov_dma[0], (unsigned long long)ov_dmab[0], (unsigned long long)ov_dma[1], (unsigned long long)ov_dmab[1], (unsigned long long)ov_told[0], (unsigned long long)ov_told[1],
                 (unsigned long long)att[0], (unsigned long long)att[1], (unsigned long long)att[2], (unsigned long long)br_pairs, (unsigned long long)br_hit, (unsigned long long)br_bytes, (unsigned long long)br_skip, sg.size(), (unsigned long long)dma_hi);
    for (int i = 0; i < ndex; i++) std::fprintf(stderr, "[s7524-dma] %s\n", dex[i]);
    for (int i = 0; i < nrex; i++) std::fprintf(stderr, "[s7524-resid] %s\n", rex[i]);
    for (int k = 0; k < 2; k++) { std::fprintf(stderr, "[s7523-op] %s", k ? "later" : "same"); for (int o = 0; o < 64; o++) if (op_b[k][o]) std::fprintf(stderr, " %02X=%llu", o, (unsigned long long)op_b[k][o]); std::fprintf(stderr, "\n"); }
}
void on_read() {
    ++reads;
    if (first_read_of_task) { first_read_of_task = false; ++entry_seen; if (busy()) ++entry_busy; }
    if (busy()) { ++busy_reads; if (++spin > max_spin) max_spin = spin; } else spin = 0;
    if (m_sv || st_pending) ++sv_reads;
    consume(g_rate);
    if ((reads & 0xFFFF) == 0) { time_t t = time(nullptr); if (t - g_last >= 5) { g_last = t; dump("periodic"); } }
}
struct Init { Init() {
    const char* e = getenv("ROGUESQ_S7523_SLOWRDP");
    if (!(e && *e && *e != '0')) return;
    unsigned a = 8, b = 0; sscanf(e, "%u,%u", &a, &b); g_rate = a ? a : 8; g_gap = b;
    rs64_s7523_on = 1;
    std::fprintf(stderr, "[s7523] finite-rate RDP model armed rate=%u B/poll gap=%u B/task\n", g_rate, g_gap);
} } g_init;
}  // namespace
extern "C" void rs64_s7523_task() { std::lock_guard<std::mutex> lk(g_mu); if ((tasks & 1023) == 0 && tasks) { time_t t = time(nullptr); if (t - g_last >= 5) { g_last = t; dump("periodic"); } }
    fs_gate(); ++tasks; consume(g_gap); first_read_of_task = true; spin = 0; }
extern "C" void rs64_s7523_start(uint32_t v) { std::lock_guard<std::mutex> lk(g_mu); m_start = v & 0xFFFFFF; m_sv = true; }
extern "C" void rs64_s7523_end(uint32_t v, const uint8_t* rdram) { std::lock_guard<std::mutex> lk(g_mu);
    if (rdram) g_rd = rdram;
    if (pre_on) { pre_on = false; uint64_t b = scan_bad(); ++br_pairs; if (b > pre_bad) { ++br_hit; br_bytes += b - pre_bad; } }
    reads_since_end = 0;
    v &= 0xFFFFFF;
    uint32_t from = m_sv ? m_start : m_end;
    const bool m_sv_was = m_sv;
    m_sv = false;
    push(from, v, m_sv_was);
    m_end = v;
    fs_gate();
}
extern "C" uint32_t rs64_s7523_cur_read() { std::lock_guard<std::mutex> lk(g_mu);
    on_read();
    uint32_t c = cur();
    if (c == last_c) { if (++same >= 4096) { same = 0; ++escapes; last_ret = c + 8; return c + 8; } } else { last_c = c; same = 0; }  // deadlock escape (as the bridge's)
    last_ret = c; ++reads_since_end;
    return c;
}
extern "C" uint32_t rs64_s7523_end_read() { std::lock_guard<std::mutex> lk(g_mu); on_read(); return m_end; }
extern "C" uint32_t rs64_s7523_status_read() { std::lock_guard<std::mutex> lk(g_mu);
    on_read();
    uint32_t s = 0x80;                     // CBUF_READY
    if (busy()) s |= 0x100 | 0x20;         // DMA_BUSY | CMD_BUSY
    if (m_sv || st_pending) s |= 0x400;  // START_VALID: a START not yet begun by the RDP
    return s;
}
extern "C" void rs64_s7523_final() { std::lock_guard<std::mutex> lk(g_mu); if (rs64_s7523_on) dump("final"); }
// s7524: called from s7094 rs64_s7094_dma_shape (before the copy) for every RSP DMA; dir 1 = DMEM->RDRAM.
extern "C" void rs64_s7523_dma(int dir, uint32_t mem, uint32_t dram, uint32_t raw, int aud) {
    if (!dir || (mem & 0x1000)) return;
    std::lock_guard<std::mutex> lk(g_mu);
    uint32_t len = raw >= 0xFFFu ? 0x1000u : raw + 1u; const uint32_t a0 = dram & 0xFFFFFF, a1 = a0 + len;
    dma_w[aud ? 1 : 0]++; if (!aud && (dram >> 24)) ++dma_hi;
    if (!aud) { for (uint32_t a = a0; a < a1 && a < (1u << 24); a++) dmabit[a >> 3] |= 1u << (a & 7); if (a0 >= m_end && a0 < m_end + 0x2000) ++ahead_w; }
    for (const S& f : sg) {
        uint32_t lo = a0 > f.lo ? a0 : f.lo, hi = a1 < f.hi ? a1 : f.hi; if (lo >= hi) continue;
        int k = aud ? 1 : 0; ov_dma[k]++; ov_dmab[k] += hi - lo;
        uint8_t* t = &tch[f.off + (lo - f.lo) - snap_base]; for (uint32_t i = 0; i < hi - lo; i++) t[i] = aud ? 2 : 1;
        bool told = lo >= last_ret && lo < m_end; ov_told[told ? 0 : 1]++;   // the last CURRENT the ucode read said these bytes were still pending
        if (ndex < 16) snprintf(dex[ndex++], sizeof dex[0], "task=%llu aud=%d raw=0x%08X dram=0x%06X len=%u seg=0x%06X-0x%06X front=0x%06X last_ret=0x%06X end=0x%06X start=0x%06X sv=%d rd_since_end=%llu qlen=%zu segs=%zu",
            (unsigned long long)tasks, aud, dram, a0, len, f.lo, f.hi, q.empty() ? 0 : q.front().lo, last_ret, m_end, m_start, m_sv, (unsigned long long)reads_since_end, q.size(), sg.size());
    }
}
extern "C" void rs64_s7523_pre_submit() { std::lock_guard<std::mutex> lk(g_mu);
    static uint64_t n = 0; if ((++n & 255) != 0) return;
    size_t qb = snap.size(); if (qb > (4u << 20)) { ++br_skip; return; }
    pre_bad = scan_bad(); pre_on = true; }
