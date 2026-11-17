// s7526 (rsp-task-v2p): same-run render-input equality of ROGUESQ_S7524_V2P on vs off.
//
// ROGUESQ_S7524_V2P=alt turns the retail _VirtualToPhysicalTask conversion on for a pseudo-random half of the gfx tasks
// (bit = splitmix64(task index) & 1, so every repeated scene gets both states regardless of how many tasks a frame has).
// Per gfx task we hash, in order, every byte the DPC bridge forwards to RT64 (rs64_rt_submit) = the exact renderer input.
// Static scenes repeat the same task stream, so a task digest seen again in a window of the last 64 tasks is a "repeat".
// Each repeat is classed by the V2P state of the two tasks: SAME (on/on or off/off) or CROSS (on/off). If V2P changes the
// RDP input, CROSS repeats are 0 while SAME repeats > 0. If V2P is invisible, CROSS ~ SAME (both states are equally likely).
// Control: ROGUESQ_S7526_TWIN=ctl also folds a constant into the digest of every V2P-on task (= "V2P-on output differs by
// one byte"): CROSS must drop to 0 in that arm while SAME stays > 0, proving the detector sees a V2P-correlated change.
// Reported per phase (rs64_phase_ord); dump rs64_s7526.log in cwd (build/) every 5 s (SIGKILL-safe).
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <ctime>
extern "C" uint32_t rs64_phase_ord(void);
extern "C" int rs64_s7526_alt = [] {
    const char* e = getenv("ROGUESQ_S7524_V2P");
    return (e && e[0] == 'a') ? 1 : 0;
}();
static const int s_ctl = [] {
    const char* e = getenv("ROGUESQ_S7526_TWIN");
    int v = (e && e[0] == 'c') ? 1 : 0;
    if (rs64_s7526_alt) fprintf(stderr, "[s7526] V2P alternating per gfx task, forwarded-byte twin digest armed%s\n", v ? " (+ctl)" : "");
    return v;
}();
namespace {
constexpr int kPh = 16, kWin = 64;
struct St { uint64_t tasks = 0, on = 0, empty = 0, rep_same = 0, rep_cross = 0, bytes = 0, uniq = 0; };
St g_st[kPh];
struct Ent { uint64_t h; int on; };
Ent g_win[kWin]; int g_wn = 0, g_wi = 0;
uint64_t g_task = 0, g_h = 0, g_n = 0; int g_on = 0; uint32_t g_ph = 0; bool g_open = false;
time_t g_last = 0;
uint64_t mix(uint64_t x) { x += 0x9E3779B97F4A7C15ull; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ull; x = (x ^ (x >> 27)) * 0x94D049BB133111EBull; return x ^ (x >> 31); }
void dump() {
    FILE* f = fopen("rs64_s7526.log", "w");
    if (!f) return;
    fprintf(f, "s7526 alt=%d ctl=%d tasks=%llu\n", rs64_s7526_alt, s_ctl, (unsigned long long)g_task);
    for (int p = 0; p < kPh; ++p) {
        const St& s = g_st[p];
        if (!s.tasks) continue;
        fprintf(f, "phase=%d tasks=%llu on=%llu empty=%llu bytes=%llu uniq=%llu rep_same=%llu rep_cross=%llu\n", p,
                (unsigned long long)s.tasks, (unsigned long long)s.on, (unsigned long long)s.empty, (unsigned long long)s.bytes,
                (unsigned long long)s.uniq, (unsigned long long)s.rep_same, (unsigned long long)s.rep_cross);
    }
    fclose(f);
}
void fold() {
    if (!g_open) return;
    St& s = g_st[g_ph < kPh ? g_ph : kPh - 1];
    ++s.tasks; s.on += g_on; s.bytes += g_n;
    if (!g_n) { ++s.empty; return; }
    uint64_t h = g_h ^ g_n * 0x100000001B3ull;
    if (s_ctl && g_on) h ^= 0x5A5A5A5A5A5A5A5Aull;
    // nearest earlier repeat in the window classifies this task
    int found = -1;
    for (int k = 1; k <= g_wn; ++k) { const Ent& e = g_win[(g_wi - k + kWin) % kWin]; if (e.h == h) { found = e.on; break; } }
    if (found < 0) ++s.uniq; else if (found == g_on) ++s.rep_same; else ++s.rep_cross;
    g_win[g_wi] = {h, g_on}; g_wi = (g_wi + 1) % kWin; if (g_wn < kWin) ++g_wn;
}
}  // namespace
// called by rs64_run_lle_gfx before the DMEM task copy; returns the V2P state for this task
extern "C" int rs64_s7526_task_begin() {
    fold();
    ++g_task;
    g_on = (int)(mix(g_task) & 1);
    g_h = 1469598103934665603ull; g_n = 0; g_ph = rs64_phase_ord(); g_open = true;
    time_t t = time(nullptr); if (t - g_last >= 5) { g_last = t; dump(); }
    return g_on;
}
extern "C" void rs64_s7526_fwd(uint32_t lo, uint32_t hi, const uint8_t* rdram) {
    if (!g_open || !rdram) return;
    lo &= 0xFFFFFF; hi = (hi - 1) % 0x1000000u + 1;
    for (uint32_t a = lo; a < hi; ++a) g_h = (g_h ^ rdram[a ^ 3]) * 1099511628211ull;
    g_n += hi > lo ? hi - lo : 0;
}
