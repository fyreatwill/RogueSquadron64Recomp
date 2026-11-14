// s7331 item 23 (reset-dangling-writer): who still writes a block after the retail scene reset frees it?
// ROGUESQ_S7331_RESETW=1 (needs ROGUESQ_S7317_ALLOCMAP=1; RSP attribution needs ROGUESQ_S7324_RCPREF, which arms the DMA hook).
// At each reset (rs64_s7325_heapsync = after coalesceFreeHeapBlocks, rs64_s7325_heaprebuild = buildHeapFreeList) upstream_compat.cpp
// hands over every host-map block the reset drops (kind H = persistent heap bulk free, R = arena rebuild, S = spill block the s7326
// release frees). Each is copied (whole data range, word-swapped rdram, compared per 64 B line) and re-compared by a poll thread every
// 8 ms for 2 s. A changed line is attributed RSP if an RSP DMA write touched it since the last poll, PI if a PI ROM DMA did (librecomp
// rs64_s4211_pi_ring), else CPU. A guest malloc whose [ptr-0x10, ptr+req+0x10) overlaps a tracked block marks it reallocated (time,
// new allocator); later changes are counted post-realloc. RSP reads of a tracked block are counted pre/post realloc too (an audio
// task reading a command list from a reallocated block is the dangerous read form). Positive control (s7330): the boot mixer buffers
// 0x80169F10/0x8016BD50 (0x1E30, CPU synth) and 0x80171EB0 (0x298, RSP voice-state write-back) must show changes; negative control:
// the dropped blocks no subsystem owns any more must stay unchanged. Detector selftest at startup: a fake block in a private buffer
// must report one changed line per writer kind and no re-fire without a new change.
// Dump: build/rs64_s7331.log, rewritten after every finished window and every 5 s (SIGKILL-safe).
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <mutex>
#include <string>
#include <thread>
#include <vector>
#include <dlfcn.h>
extern "C" volatile uint8_t* volatile g_recomp_rdram_for_wp_raw;
struct Rs64S4211Pi { uint32_t dram, size, rom_off, phase, pc; };
extern Rs64S4211Pi rs64_s4211_pi_ring[8192];
extern uint64_t rs64_s4211_pi_n;
extern "C" int rs64_s7331_on = [] {
    const char* e = getenv("ROGUESQ_S7331_RESETW");
    const int v = (e && *e && *e != '0') ? 1 : 0;
    if (v) fprintf(stderr, "[s7331] reset dangling-writer audit armed (allocmap=%s rcpref=%s)\n",
                   getenv("ROGUESQ_S7317_ALLOCMAP") ? getenv("ROGUESQ_S7317_ALLOCMAP") : "(unset: no blocks)",
                   getenv("ROGUESQ_S7324_RCPREF") ? getenv("ROGUESQ_S7324_RCPREF") : "(unset: no RSP attribution)");
    return v;
}();
struct S7325Out { uint32_t lo, loend, hi, lreq, hreq; void* lopc[3]; void* hipc[3]; uint32_t fptr, freq; double fage; void* fpc[4]; void* apc[3];
                  int gk; uint32_t gfl, gh, gsz; };
extern "C" int rs64_s7325_gap(uint32_t x, S7325Out* o, int guest);
namespace {
constexpr double kWin = 2.0;
constexpr uint32_t kLine = 64;
enum { W_CPU, W_RSP, W_PI, W_N };
const char* kW[W_N] = {"cpu", "rsp", "pi"};
struct Blk {
    uint64_t sync; char kind; uint32_t ptr, req; void* own; double t0;
    std::vector<uint8_t> copy; std::vector<uint8_t> mark;  // per line: bit0 RSP wr, bit1 PI since last poll
    double trealloc = -1; uint32_t rptr = 0, rreq = 0; void* rown = nullptr;
    uint32_t lines[2][W_N] = {}, events[2][W_N] = {};     // [pre/post realloc][writer]: distinct lines changed / change events
    double first[2][W_N] = {{-1, -1, -1}, {-1, -1, -1}}; uint32_t firstoff[2][W_N] = {};
    uint64_t rsp_rd[2] = {}, rsp_wr[2] = {};
    int gk[2][W_N] = {{-1, -1, -1}, {-1, -1, -1}}; uint32_t gfl[2][W_N] = {}, gh[2][W_N] = {}, gsz[2][W_N] = {}; int hk[2][W_N] = {};  // guest heap walk + host class at first change
    std::vector<uint8_t> seen;  // per line: bit (pre/post*3 + writer) set once
    bool done = false;
};
std::mutex g_mu;
std::vector<Blk*> g_act, g_fin;
uint64_t g_nsync = 0, g_ntrack = 0, g_nbytes = 0, g_pi_seen = 0;
std::atomic<bool> g_thr{false};
double now_s() { return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count(); }
std::string sym(void* pc) {
    Dl_info di; char b[160];
    if (pc && dladdr(pc, &di) && di.dli_sname) snprintf(b, sizeof b, "%s+0x%lx", di.dli_sname, (unsigned long)((char*)pc - (char*)di.dli_saddr));
    else snprintf(b, sizeof b, "?%p", pc);
    return b;
}
inline uint32_t phys(uint32_t a) { return a & 0x1FFFFFFu; }
// mark lines of every active block overlapping [p, p+len) (phys) with bit m
void mark_locked(uint32_t p, uint32_t len, uint8_t m) {
    for (Blk* b : g_act) {
        const uint32_t bp = phys(b->ptr), be = bp + b->req;
        if (p >= be || p + len <= bp) continue;
        const uint32_t s = (p > bp ? p - bp : 0) / kLine, e = (std::min(p + len, be) - bp - 1) / kLine;
        for (uint32_t k = s; k <= e && k < b->mark.size(); ++k) b->mark[k] |= m;
    }
}
void compare_locked(Blk* b, const uint8_t* r, double t) {
    const int ph = b->trealloc >= 0 ? 1 : 0;
    const uint32_t nl = (uint32_t)b->mark.size();
    for (uint32_t k = 0; k < nl; ++k) {
        const uint32_t off = k * kLine, n = std::min(kLine, b->req - off);
        uint8_t* c = b->copy.data() + off;
        const uint8_t* g = r + phys(b->ptr) + off;
        if (memcmp(c, g, n) != 0) {
            const int w = (b->mark[k] & 1) ? W_RSP : (b->mark[k] & 2) ? W_PI : W_CPU;
            b->events[ph][w]++;
            const uint8_t bit = (uint8_t)(1u << (ph * 3 + w));
            if (!(b->seen[k] & bit)) { b->seen[k] |= bit; b->lines[ph][w]++; }
            if (b->first[ph][w] < 0) { b->first[ph][w] = t - b->t0; b->firstoff[ph][w] = off;
                if (b->kind != 'T') { S7325Out o{}; o.gk = -1; b->hk[ph][w] = rs64_s7325_gap(b->ptr + off, &o, 1);
                    b->gk[ph][w] = o.gk; b->gfl[ph][w] = o.gfl; b->gh[ph][w] = o.gh; b->gsz[ph][w] = o.gsz; } }
            memcpy(c, g, n);
        }
        b->mark[k] = 0;
    }
}
void dump_locked() {
    FILE* o = fopen("rs64_s7331.log", "w"); if (!o) return;
    uint64_t chpre = 0, chpost = 0, unch = 0, re = 0; uint64_t wpre[W_N] = {}, wpost[W_N] = {};
    std::vector<Blk*> all(g_fin); all.insert(all.end(), g_act.begin(), g_act.end());
    for (Blk* b : all) {
        bool p0 = false, p1 = false;
        for (int w = 0; w < W_N; ++w) { if (b->lines[0][w]) { p0 = true; wpre[w]++; } if (b->lines[1][w]) { p1 = true; wpost[w]++; } }
        if (b->trealloc >= 0) ++re; if (p0) ++chpre; if (p1) ++chpost; if (!p0 && !p1) ++unch;
    }
    fprintf(o, "s7331 syncs=%llu tracked=%llu bytes=0x%llX finished=%zu active=%zu pi_seen=%llu | changed_pre=%llu (cpu %llu rsp %llu pi %llu) "
               "changed_post=%llu (cpu %llu rsp %llu pi %llu) unchanged=%llu reallocated=%llu\n",
            (unsigned long long)g_nsync, (unsigned long long)g_ntrack, (unsigned long long)g_nbytes, g_fin.size(), g_act.size(), (unsigned long long)g_pi_seen,
            (unsigned long long)chpre, (unsigned long long)wpre[0], (unsigned long long)wpre[1], (unsigned long long)wpre[2],
            (unsigned long long)chpost, (unsigned long long)wpost[0], (unsigned long long)wpost[1], (unsigned long long)wpost[2],
            (unsigned long long)unch, (unsigned long long)re);
    // per changed block (or RSP-touched) one row; unchanged blocks summarised per (sync, kind)
    std::map<std::pair<uint64_t, char>, std::pair<uint64_t, uint64_t>> quiet;
    for (Blk* b : all) {
        bool any = b->rsp_rd[0] || b->rsp_rd[1] || b->rsp_wr[0] || b->rsp_wr[1];
        for (int ph = 0; ph < 2; ++ph) for (int w = 0; w < W_N; ++w) if (b->lines[ph][w]) any = true;
        if (!any) { auto& q = quiet[{b->sync, b->kind}]; q.first++; q.second += b->req; continue; }
        fprintf(o, "B sync=%llu kind=%c ptr=%08X req=0x%X own=%s t0=%.6f", (unsigned long long)b->sync, b->kind, b->ptr, b->req, sym(b->own).c_str(), b->t0);
        if (b->trealloc >= 0) fprintf(o, " realloc=+%.1fms tr=%.6f new=%08X+0x%X by=%s", (b->trealloc - b->t0) * 1e3, b->trealloc, b->rptr, b->rreq, sym(b->rown).c_str());
        for (int ph = 0; ph < 2; ++ph) for (int w = 0; w < W_N; ++w) if (b->lines[ph][w])
            fprintf(o, " %s_%s=%u/%u@+%.1fms off=0x%X g=%d:%X:%08X:%X h=%d", ph ? "post" : "pre", kW[w], b->lines[ph][w], b->events[ph][w], b->first[ph][w] * 1e3, b->firstoff[ph][w],
                    b->gk[ph][w], b->gfl[ph][w], b->gh[ph][w], b->gsz[ph][w], b->hk[ph][w]);
        fprintf(o, " rsp_rd=%llu/%llu rsp_wr=%llu/%llu\n", (unsigned long long)b->rsp_rd[0], (unsigned long long)b->rsp_rd[1],
                (unsigned long long)b->rsp_wr[0], (unsigned long long)b->rsp_wr[1]);
    }
    for (auto& kv : quiet) fprintf(o, "Q sync=%llu kind=%c unchanged=%llu bytes=0x%llX\n", (unsigned long long)kv.first.first, kv.first.second,
                                   (unsigned long long)kv.second.first, (unsigned long long)kv.second.second);
    fclose(o);
}
void poll() {
    uint64_t pi_last = rs64_s4211_pi_n; double last_dump = now_s();
    for (;;) {
        std::this_thread::sleep_for(std::chrono::milliseconds(8));
        const uint8_t* r = (const uint8_t*)g_recomp_rdram_for_wp_raw; if (!r) continue;
        const double t = now_s();
        std::lock_guard<std::mutex> lk(g_mu);
        const uint64_t pn = rs64_s4211_pi_n;
        if (pn - pi_last > 8192) pi_last = pn - 8192;
        for (; pi_last < pn; ++pi_last) { const Rs64S4211Pi& e = rs64_s4211_pi_ring[pi_last % 8192]; ++g_pi_seen; mark_locked(e.dram, e.size, 2); }
        bool fin = false;
        for (size_t i = 0; i < g_act.size();) {
            Blk* b = g_act[i]; compare_locked(b, r, t);
            if (t - b->t0 >= kWin) { b->copy.clear(); b->copy.shrink_to_fit(); b->mark.clear(); b->seen.clear(); b->done = true;
                g_fin.push_back(b); g_act[i] = g_act.back(); g_act.pop_back(); fin = true; continue; }
            ++i;
        }
        if (fin || t - last_dump >= 5) { last_dump = t; dump_locked(); }
    }
}
// selftest: fake block in a private buffer, one change per writer kind must be attributed
const bool g_selftest = [] {
    if (!rs64_s7331_on) return true;
    std::vector<uint8_t> mem(0x400, 0); Blk b; b.ptr = 0x80000100u; b.req = 0x200; b.t0 = 0; b.sync = 0; b.kind = 'T'; b.own = nullptr;
    b.copy.assign(mem.begin() + 0x100, mem.begin() + 0x300); b.mark.assign(8, 0); b.seen.assign(8, 0);
    mem[0x100 + 0x10] = 1;                     // cpu
    mem[0x100 + 0x80] = 2; b.mark[2] = 1;      // rsp
    mem[0x100 + 0x1C0] = 3; b.mark[7] = 2;     // pi
    compare_locked(&b, mem.data() - 0x0 , 1.0);  // r indexed by phys: phys(ptr)=0x100
    const bool ok = b.lines[0][W_CPU] == 1 && b.lines[0][W_RSP] == 1 && b.lines[0][W_PI] == 1 && b.firstoff[0][W_RSP] == 0x80;
    compare_locked(&b, mem.data(), 1.1);
    const bool ok2 = b.events[0][W_CPU] == 1;  // no re-fire without a new change
    fprintf(stderr, "[s7331] selftest %s (cpu %u rsp %u pi %u, refire %s)\n", ok && ok2 ? "pass" : "FAIL", b.lines[0][W_CPU], b.lines[0][W_RSP],
            b.lines[0][W_PI], ok2 ? "no" : "YES");
    return ok && ok2;
}();
}  // namespace
// one dropped block (called by upstream_compat.cpp at each reset, outside its own map lock)
extern "C" void rs64_s7331_track(uint64_t sync, char kind, uint32_t ptr, uint32_t req, void* own) {
    if (!rs64_s7331_on || !req || req > 0x800000u) return;
    const uint8_t* r = (const uint8_t*)g_recomp_rdram_for_wp_raw; if (!r) return;
    if (phys(ptr) + req > 0x1800000u) return;
    Blk* b = new Blk; b->sync = sync; b->kind = kind; b->ptr = ptr; b->req = req; b->own = own; b->t0 = now_s();
    b->copy.assign(r + phys(ptr), r + phys(ptr) + req); const uint32_t nl = (req + kLine - 1) / kLine; b->mark.assign(nl, 0); b->seen.assign(nl, 0);
    std::lock_guard<std::mutex> lk(g_mu); g_act.push_back(b); ++g_ntrack; g_nbytes += req;
    if (!g_thr.exchange(true)) std::thread(poll).detach();
}
extern "C" void rs64_s7331_sync(uint64_t sync) { if (!rs64_s7331_on) return; std::lock_guard<std::mutex> lk(g_mu); if (sync > g_nsync) g_nsync = sync; }
extern "C" void rs64_s7331_malloc(uint32_t ptr, uint32_t req, void* own) {
    if (!rs64_s7331_on || !ptr) return;
    std::lock_guard<std::mutex> lk(g_mu); if (g_act.empty()) return;
    const uint32_t lo = phys(ptr) - 0x10, hi = phys(ptr) + req + 0x10; const double t = now_s();
    const uint8_t* r = (const uint8_t*)g_recomp_rdram_for_wp_raw;
    for (Blk* b : g_act) {
        if (b->trealloc >= 0) continue;
        const uint32_t bp = phys(b->ptr), be = bp + b->req;
        if (lo >= be || hi <= bp) continue;
        if (r) compare_locked(b, r, t);  // close the pre-realloc phase on what is there now (header writes land in pre: see report)
        b->trealloc = t; b->rptr = ptr; b->rreq = req; b->rown = own;
    }
}
// RSP DMA (raw dram, inclusive len as passed to the s7094 hook)
extern "C" void rs64_s7331_dma(int dir, uint32_t dram, uint32_t raw_len) {
    if (!rs64_s7331_on) return;
    const uint32_t p = phys(dram) & ~7u, len = (raw_len & 0xFFFu) + 1;
    std::lock_guard<std::mutex> lk(g_mu); if (g_act.empty()) return;
    for (Blk* b : g_act) {
        const uint32_t bp = phys(b->ptr), be = bp + b->req;
        if (p >= be || p + len <= bp) continue;
        const int ph = b->trealloc >= 0 ? 1 : 0;
        if (dir) b->rsp_wr[ph]++; else b->rsp_rd[ph]++;
    }
    if (dir) mark_locked(p, len, 1);
}
