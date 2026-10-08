"""s4215: dump the full OSTask as raw guest words (plus guest address, 0x10 bytes before) at run_task entry. Env ROGUESQ_LOG_S4213=1."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
rsp = R / "lib/N64ModernRuntime/librecomp/src/rsp.cpp"
t = rsp.read_text()
if "rs64_s4215_dump" not in t:
    anchor = "bool recomp::rsp::run_task(uint8_t* rdram, const OSTask* task) {\n"
    assert t.count(anchor) == 1
    fn = r'''static void rs64_s4215_dump(uint8_t* rdram, const OSTask* task) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4213"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    static uint32_t ph_key = 0xFFFFFFFFu; static unsigned cnt;
    uint32_t phase = rs64_phase_ord();
    if (phase != ph_key) { ph_key = phase; cnt = 0; }
    unsigned n = ++cnt;
    if (!(n <= 3 || n == 64 || n == 512)) return;
    uint32_t ga = (uint32_t)((const uint8_t*)task - rdram);
    std::fprintf(stderr, "[s4215-task] phase=%u n=%u task_off=0x%X ctl_type=%u\n", phase, n, ga, (unsigned)task->t.type);
    for (int row = -4; row < 20; row++) {
        uint32_t a = ga + row * 4;
        uint32_t w = (uint32_t)rdram[(a + 0) ^ 3] << 24 | (uint32_t)rdram[(a + 1) ^ 3] << 16 | (uint32_t)rdram[(a + 2) ^ 3] << 8 | rdram[(a + 3) ^ 3];
        std::fprintf(stderr, "[s4215-w] phase=%u n=%u off=%+d w=0x%08X\n", phase, n, row * 4, w);
    }
}
'''
    t = t.replace(anchor, fn + anchor + "    rs64_s4215_dump(rdram, task);\n")
    rsp.write_text(t); print("patched")
