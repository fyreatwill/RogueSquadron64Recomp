#!/usr/bin/env python3
"""s4735: add ROGUESQ_DLWALK jump trace to src/rsp/dpc_bridge.cpp (idempotent)."""
p = 'src/rsp/dpc_bridge.cpp'
s = open(p).read()
if 'dlwalk_on' in s:
    raise SystemExit('already patched')

trace = '''
// s4735 DL-walk jump trace (ROGUESQ_DLWALK=1): record every non-sequential fetch
// and every DL call/return so a runaway task's backward jump can be attributed.
struct DlWalkTrace {
    struct Ev { uint32_t kind, a, b, c, n; };  // 1 nonseq-fetch(prev,addr,prevop) 2 push 3 pop
    uint32_t task = 0, fetches = 0, nonseq = 0, back = 0, prev = 0xFFFFFFFFu, prev_op = 0;
    std::vector<Ev> ev;
};
static DlWalkTrace g_dlw;
static bool dlwalk_on() {
    static const bool on = [] { const char *e = std::getenv("ROGUESQ_DLWALK"); return e && *e && *e != '0'; }();
    return on;
}
static void dlw_event(uint32_t kind, uint32_t a, uint32_t b, uint32_t c) {
    if (g_dlw.ev.size() < 400) g_dlw.ev.push_back({kind, a, b, c, g_dlw.fetches});
}
'''
def rep(old, new):
    global s
    assert old in s, old[:50]
    s = s.replace(old, new, 1)

rep('static bool log_e9_provenance() {', trace + '\nstatic bool log_e9_provenance() {')
rep('extern "C" void rs64_e9prov_source_fetch(uint32_t guest_addr, uint32_t w0) {\n',
'''extern "C" void rs64_e9prov_source_fetch(uint32_t guest_addr, uint32_t w0) {
    if (dlwalk_on()) {
        const uint32_t a = guest_addr & 0x7FFFFFu;
        ++g_dlw.fetches;
        if (g_dlw.prev != 0xFFFFFFFFu && a != g_dlw.prev + 8) {
            ++g_dlw.nonseq;
            if (a < g_dlw.prev) ++g_dlw.back;
            dlw_event(1, g_dlw.prev, a, g_dlw.prev_op);
        }
        g_dlw.prev = a; g_dlw.prev_op = w0 >> 24;
    }
''')
rep('    g_e9prov = {};\n    {\n        std::lock_guard<std::mutex> lock(g_f5_vtxcolor_mutex);',
    '    g_e9prov = {};\n    if (dlwalk_on()) { g_dlw = {}; g_dlw.task = task; }\n    {\n        std::lock_guard<std::mutex> lock(g_f5_vtxcolor_mutex);')
rep('uint32_t caller, uint32_t w0, uint32_t w1) {\n    rs64_e9prov_frame_event(1',
    'uint32_t caller, uint32_t w0, uint32_t w1) {\n    if (dlwalk_on()) dlw_event(2, slot, saved_target & 0x7FFFFFu, saved_pc & 0x7FFFFFu);\n    rs64_e9prov_frame_event(1')
rep('extern "C" void rs64_e9prov_frame_pop(uint32_t slot, uint32_t saved_target, uint32_t saved_pc) {\n',
    'extern "C" void rs64_e9prov_frame_pop(uint32_t slot, uint32_t saved_target, uint32_t saved_pc) {\n    if (dlwalk_on()) dlw_event(3, slot, saved_target & 0x7FFFFFu, saved_pc & 0x7FFFFFu);\n')
rep('extern "C" void rs64_e9prov_task_end(uint32_t task) {\n',
'''extern "C" void rs64_e9prov_task_end(uint32_t task) {
    if (dlwalk_on() && g_dlw.task == task) {
        static int sums = 0, dets = 0;
        if (sums < 400 && (g_dlw.fetches > 3000 || sums < 30)) {
            ++sums;
            fprintf(stderr, "[dlwalk-sum] task=%u phase=%u fetches=%u nonseq=%u back=%u events=%zu\\n",
                    task, rs64_phase_ord(), g_dlw.fetches, g_dlw.nonseq, g_dlw.back, g_dlw.ev.size());
        }
        if (g_dlw.fetches > 3000 && dets < 6) {
            ++dets;
            for (const auto& e : g_dlw.ev)
                fprintf(stderr, "[dlwalk-ev] task=%u n=%u k=%u a=0x%06X b=0x%06X c=0x%06X\\n", task, e.n, e.kind, e.a, e.b, e.c);
        }
        fflush(stderr);
    }
''')
open(p, 'w').write(s)
print('patched')
