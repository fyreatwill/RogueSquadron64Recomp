// s7095: passive differential of the RSP-side DPC register model (include/rsp_dpc_macros.h + dpc_bridge.cpp
// rs64_dpc_current_read) against a hardware shadow model of the same registers (n64brew RDP / DPC registers,
// angrylion / parallel-rdp DPC handling), assuming an RDP that consumes instantly (ours does):
//   mtc0 DPC_START v : START=v, STATUS.START_VALID=1; CURRENT is NOT touched (ours snaps CURRENT=v)
//   mtc0 DPC_END v   : if START_VALID { CURRENT=START; START_VALID=0 }; END=v; RDP consumes -> CURRENT=v
//   mtc0 DPC_STATUS  : only bit0 (clear XBUS) / bit1 (set XBUS) matter to this ucode; the ucode only writes 0x1
//   state PERSISTS across tasks (ours is zeroed per gfx task by rs64_dpc_reset)
// At every ucode read it compares our value with the shadow, by context: 'entry' (task started, no END yet),
// 'pend' (START written, END not yet), 'other'. It also evaluates the two wrap-path wait predicates the ucode runs
// against CURRENT on the shadow (L_115C: spin while CURRENT == new START; L_116C: spin while CURRENT is inside
// (START, START+len]) and counts bounded-poll escapes (rs64_dpc_current_read returning v+8).
// ROGUESQ_S7095_DPC=1 arms it; dump to build/rs64_s7095.log every 5 s (SIGKILL-safe). Self-test at init is the
// detector positive control (each predicate fires on a crafted sequence, the escape fires once per 64 polls).
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
extern "C" int rs64_s7095_on = [] {
    const char* e = getenv("ROGUESQ_S7095_DPC");
    int v = (e && *e && *e != '0') ? 1 : 0;
    if (v) fprintf(stderr, "[s7095] dpc register model differential armed\n");
    return v;
}();
uint32_t rs64_dpc_current_read();
extern "C" void rs64_dpc_reset();
extern uint32_t g_rsp_dpc_current;
namespace {
struct Model { uint32_t start = 0, end = 0, cur = 0; bool sv = false, xbus = false, task_end = false; };
enum { C_ENTRY, C_PEND, C_OTHER, C_N };
const char* kCtx[C_N] = {"entry", "pend", "other"};
struct Stats {
    uint64_t tasks = 0, starts = 0, ends = 0, status_w = 0, status_w_setx = 0, cur_reads = 0, end_reads = 0, status_reads = 0;
    uint64_t cur_div[C_N] = {}, end_div[C_N] = {}, st_sv_div = 0, st_x_div = 0, escapes = 0, spin115 = 0, spin116 = 0;
    uint64_t sv_at_task = 0, wraps = 0, laps = 0, hw_cur_ne_end_at_entry = 0, hw_resume_possible = 0;
    uint64_t max_len = 0; uint32_t ex115_start = 0, ex116_start = 0, ex116_cur = 0, ex116_len = 0;
};
Model g_m; Stats g_s; time_t g_last = 0;
int ctx(const Model& m) { return m.sv ? C_PEND : (!m.task_end ? C_ENTRY : C_OTHER); }
void on_start(Model& m, Stats& s, uint32_t v) {
    s.starts++;
    if (m.task_end) s.wraps++;
    if (m.cur == v && m.task_end) { if (!s.spin115) s.ex115_start = v; s.spin115++; }
    m.start = v; m.sv = true;
}
void on_end(Model& m, Stats& s, uint32_t v) {
    s.ends++;
    if (m.sv) {
        const uint32_t len = v - m.start;
        if (len > s.max_len) s.max_len = len;
        if ((int32_t)(m.start - m.cur) < 0 && (int32_t)(m.start + len - m.cur) >= 0) {
            if (!s.spin116) { s.ex116_start = m.start; s.ex116_cur = m.cur; s.ex116_len = len; }
            s.spin116++;
        }
        m.cur = m.start; m.sv = false;
    } else if ((int32_t)(v - m.end) < 0) s.laps++;
    m.end = v; m.cur = v; m.task_end = true;
}
void dump() {
    FILE* o = fopen("rs64_s7095.log", "w");
    if (!o) return;
    const Stats& s = g_s;
    fprintf(o, "s7095 tasks=%llu starts=%llu ends=%llu wraps=%llu laps=%llu max_len=0x%llX status_w=%llu status_w_setx=%llu\n",
            (unsigned long long)s.tasks, (unsigned long long)s.starts, (unsigned long long)s.ends, (unsigned long long)s.wraps,
            (unsigned long long)s.laps, (unsigned long long)s.max_len, (unsigned long long)s.status_w, (unsigned long long)s.status_w_setx);
    fprintf(o, "READS cur=%llu end=%llu status=%llu escapes=%llu\n", (unsigned long long)s.cur_reads,
            (unsigned long long)s.end_reads, (unsigned long long)s.status_reads, (unsigned long long)s.escapes);
    for (int c = 0; c < C_N; c++)
        fprintf(o, "DIV ctx=%s cur=%llu end=%llu\n", kCtx[c], (unsigned long long)s.cur_div[c], (unsigned long long)s.end_div[c]);
    fprintf(o, "STATUS start_valid_div=%llu xbus_div=%llu sv_pending_at_task=%llu\n", (unsigned long long)s.st_sv_div,
            (unsigned long long)s.st_x_div, (unsigned long long)s.sv_at_task);
    fprintf(o, "HWWAIT spin115=%llu (ex start=0x%X) spin116=%llu (ex start=0x%X cur=0x%X len=0x%X) hw_cur_ne_end_at_entry=%llu\n",
            (unsigned long long)s.spin115, s.ex115_start, (unsigned long long)s.spin116, s.ex116_start, s.ex116_cur, s.ex116_len,
            (unsigned long long)s.hw_cur_ne_end_at_entry);
    fclose(o);
}
// Positive control: the detector must fire on crafted sequences and stay silent on the ucode's normal shape.
const bool g_selftest = [] {
    if (!rs64_s7095_on) return true;
    int bad = 0;
    { Model m; Stats s; m.task_end = true; on_end(m, s, 0x2000);           // old END near the ring top
      on_start(m, s, 0x1000); on_end(m, s, 0x1100);                        // normal wrap: shadow CURRENT 0x2000 outside (0x1000,0x1100]
      if (s.spin116 || s.spin115) bad++;
      on_end(m, s, 0x1F00); on_start(m, s, 0x1E80); on_end(m, s, 0x1F80);  // crafted: CURRENT 0x1F00 inside (0x1E80,0x1F80]
      if (s.spin116 != 1) bad++;
      on_start(m, s, 0x1F80); on_end(m, s, 0x1F90);                        // crafted: START == shadow CURRENT
      if (s.spin115 != 1) bad++; }
    { const uint32_t save = g_rsp_dpc_current; rs64_dpc_reset(); uint32_t esc = 0;
      for (int i = 0; i < 130; i++) if (rs64_dpc_current_read() != g_rsp_dpc_current) esc++;
      if (esc != 2) bad++; rs64_dpc_reset(); g_rsp_dpc_current = save; }
    fprintf(stderr, "[s7095] selftest %s (%d bad of 4)\n", bad ? "FAIL" : "pass", bad);
    g_s = Stats{}; g_m = Model{};
    return bad == 0;
}();
void maybe_dump() { time_t t = time(nullptr); if (t - g_last >= 5) { g_last = t; dump(); } }
}  // namespace
extern "C" void rs64_s7095_task() {
    g_s.tasks++;
    if (g_m.sv) g_s.sv_at_task++;
    if (g_m.cur != g_m.end) g_s.hw_cur_ne_end_at_entry++;
    g_m.task_end = false;
    maybe_dump();
}
extern "C" void rs64_s7095_start(uint32_t v) { on_start(g_m, g_s, v); }
extern "C" void rs64_s7095_end(uint32_t v) { on_end(g_m, g_s, v); }
extern "C" void rs64_s7095_status_write(uint32_t v) {
    g_s.status_w++;
    if (v & 2) { g_s.status_w_setx++; g_m.xbus = true; }
    if (v & 1) g_m.xbus = false;
}
extern "C" void rs64_s7095_cur_read(uint32_t ours, int escaped) {
    g_s.cur_reads++;
    if (escaped) g_s.escapes++;
    if (ours != g_m.cur) g_s.cur_div[ctx(g_m)]++;
}
extern "C" void rs64_s7095_end_read(uint32_t ours) { g_s.end_reads++; if (ours != g_m.end) g_s.end_div[ctx(g_m)]++; }
extern "C" void rs64_s7095_status_read() {
    g_s.status_reads++;
    if (g_m.sv) g_s.st_sv_div++;
    if (g_m.xbus) g_s.st_x_div++;
}
