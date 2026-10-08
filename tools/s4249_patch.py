#!/usr/bin/env python3
"""s4249: install the g_lle_task_mutex per-holder hold-time census into src/main/main.cpp (idempotent)."""
p = 'src/main/main.cpp'
s = open(p).read()
if 's4249::' in s:
    raise SystemExit('already applied')

old = '''extern "C" void rs64_dmem_lock()   { g_lle_task_mutex.lock(); }
extern "C" void rs64_dmem_unlock() { g_lle_task_mutex.unlock(); }
'''
new = r'''// s4249: per-holder hold-time census of g_lle_task_mutex (outermost holds only).
// Tags: 0=audio run_task (DmemGuard), 1=rs64_run_lle_gfx, 2=factor5_gfx_runner (outermost,
// i.e. not nested in 1). Enabled by ROGUESQ_S4245. Prints each hold >=3 ms and a 3 s summary.
namespace s4249 {
static thread_local int t_depth = 0;
static thread_local int t_tag = 0;
static thread_local std::chrono::steady_clock::time_point t_t0;
static const bool on = [] { const char* e = std::getenv("ROGUESQ_S4245"); return e && e[0] && e[0] != '0'; }();
static const auto T0 = std::chrono::steady_clock::now();
static const char* const names[3] = {"audio", "run_lle_gfx", "gfx_runner"};
struct Agg { uint64_t n = 0, sum_us = 0, max_us = 0, over1ms = 0; };
static std::mutex agg_mu;
static Agg agg[3];
static double last_print = 0;
static void acquired(int tag) {
    if (!on) return;
    if (t_depth++ == 0) { t_tag = tag; t_t0 = std::chrono::steady_clock::now(); }
}
static void released() {
    if (!on) return;
    if (--t_depth != 0) return;
    auto now = std::chrono::steady_clock::now();
    uint64_t us = (uint64_t)std::chrono::duration_cast<std::chrono::microseconds>(now - t_t0).count();
    double t = std::chrono::duration<double>(now - T0).count();
    std::lock_guard<std::mutex> g(agg_mu);
    Agg& a = agg[t_tag]; a.n++; a.sum_us += us; if (us > a.max_us) a.max_us = us; if (us >= 1000) a.over1ms++;
    if (us >= 3000)
        std::fprintf(stderr, "[s4249-hold] t=%.3f tag=%s hold_us=%llu\n", t, names[t_tag], (unsigned long long)us);
    if (t - last_print >= 3.0) {
        for (int i = 0; i < 3; ++i) {
            std::fprintf(stderr, "[s4249-sum] t=%.1f tag=%s n=%llu sum_us=%llu max_us=%llu over1ms=%llu\n", t, names[i],
                (unsigned long long)agg[i].n, (unsigned long long)agg[i].sum_us, (unsigned long long)agg[i].max_us, (unsigned long long)agg[i].over1ms);
            agg[i] = Agg{};
        }
        last_print = t;
    }
}
struct Hold { explicit Hold(int tag) { acquired(tag); } ~Hold() { released(); } };
}

extern "C" void rs64_dmem_lock()   { g_lle_task_mutex.lock(); s4249::acquired(0); }
extern "C" void rs64_dmem_unlock() { s4249::released(); g_lle_task_mutex.unlock(); }
'''
assert old in s
s = s.replace(old, new)

a = '''static RspExitReason factor5_gfx_runner(uint8_t* rdram, uint32_t ucode_addr) {
    std::lock_guard<std::recursive_mutex> lle_lock(g_lle_task_mutex);
'''
assert a in s
s = s.replace(a, a + '    s4249::Hold s4249_hold(2);\n')
b = '''extern "C" int rs64_run_lle_gfx(uint8_t* rdram, const OSTask* task) {
    std::lock_guard<std::recursive_mutex> lle_lock(g_lle_task_mutex);
'''
assert b in s
s = s.replace(b, b + '    s4249::Hold s4249_hold(1);\n')
open(p, 'w').write(s)
print('applied')
