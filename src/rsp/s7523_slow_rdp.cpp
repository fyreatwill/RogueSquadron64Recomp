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
            if (bad) {
                if (h.ctl) { ctl_caught++; h.ctl = false; }
                else { over_bytes += bad; over_ranges++; { uint64_t a = tasks - h.task; int k = a == 0 ? 0 : a == 1 ? 1 : 2; over_age[k]++; over_age_b[k] += bad; } { int k2 = (tasks == h.task) ? 0 : 1; for (uint32_t i = 0; i < take; i++) if (g_rd[(h.lo + i) ^ 3] != s[i]) { uint32_t a = (h.lo + i) & ~7u; uint32_t si = a >= h.lo ? 0 : 0; (void)si; op_b[k2][g_rd[a ^ 3] & 0x3F]++; } }
                  if (nex < 16) { char hx[2][20]; for (int w = 0; w < 2; w++) for (uint32_t i = 0; i < 8 && i < take; i++) snprintf(hx[w] + 2 * i, 3, "%02X", w ? g_rd[(h.lo + i) ^ 3] : s[i]); hx[0][2*(take<8?take:8)] = hx[1][2*(take<8?take:8)] = 0;
                    snprintf(ex[nex++], sizeof ex[0], "task=%llu push=%llu lo=0x%06X take=%u bad=%u snap=%s now=%s", (unsigned long long)tasks, (unsigned long long)h.task, h.lo, take, bad, hx[0], hx[1]); } }
            }
        }
        h.lo += take; h.off += take; n -= take; consumed += take;
        if (h.lo == h.hi) {
            if (h.ctl) h.ctl = false;   // a planted flip in a range never compared would be a ctl miss (counted below)
            q.pop_front();
            if (!q.empty() && q.front().st) --st_pending;
            if (q.empty()) { snap.clear(); snap_base = 0; }
            else if (q.front().off - snap_base > (1u << 20)) { size_t d = q.front().off - snap_base; snap.erase(snap.begin(), snap.begin() + d); snap_base += d; }
        }
    }
}
void push(uint32_t lo, uint32_t hi, bool st) {
    if (hi < lo || hi - lo > 0x100000u || !g_rd) { ++skipped; return; }
    if (hi == lo && !st) return;
    if (q.empty()) { snap.clear(); snap_base = 0; }
    R r{lo, hi, snap_base + snap.size(), false, st, tasks};
    if (st && !q.empty()) ++st_pending;
    for (uint32_t a = lo; a < hi; a++) snap.push_back(g_rd[a ^ 3]);
    if (hi > lo && ++ranges % 997 == 0) { snap[r.off - snap_base] ^= 0x5A; r.ctl = true; ctl_planted++; }
    q.push_back(r);
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
    if (c == last_c) { if (++same >= 4096) { same = 0; ++escapes; return c + 8; } } else { last_c = c; same = 0; }  // deadlock escape (as the bridge's)
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
