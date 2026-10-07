"""s4213: per-task census at recomp::rsp::run_task entry for ALL task types (gfx+audio): type, boot/ucode/ucode_data ptrs, data_ptr/size, guest pc. Env ROGUESQ_LOG_S4213=1."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
rsp = R / "lib/N64ModernRuntime/librecomp/src/rsp.cpp"
t = rsp.read_text()
if "rs64_s4213_census" not in t:
    anchor = "bool recomp::rsp::run_task(uint8_t* rdram, const OSTask* task) {\n"
    assert t.count(anchor) == 1
    fn = r'''extern "C" volatile uint32_t g_rs64_last_guest_pc;
static void rs64_s4213_census(const OSTask* task) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4213"); return e && e[0] && e[0] != '0'; }();
    if (!on) return;
    static uint32_t ph_key = 0xFFFFFFFFu; static unsigned cnt[16]; static unsigned total;
    uint32_t phase = rs64_phase_ord();
    if (phase != ph_key) { ph_key = phase; for (auto& c : cnt) c = 0; total = 0; }
    uint32_t ty = static_cast<uint32_t>(task->t.type);
    total++; unsigned n = ++cnt[ty & 15];
    if (n <= 6 || (n & (n - 1)) == 0) {
        std::fprintf(stderr, "[s4213-task] phase=%u type=%u n=%u total=%u flags=0x%X boot=0x%08X/%X ucode=0x%08X/%X udata=0x%08X/%X data_ptr=0x%08X/%X yield=0x%08X pc=0x%08X\n",
            phase, ty, n, total, (unsigned)task->t.flags,
            (uint32_t)task->t.ucode_boot, (unsigned)task->t.ucode_boot_size,
            (uint32_t)task->t.ucode, (unsigned)task->t.ucode_size,
            (uint32_t)task->t.ucode_data, (unsigned)task->t.ucode_data_size,
            (uint32_t)task->t.data_ptr, (unsigned)task->t.data_size,
            (uint32_t)task->t.yield_data_ptr, (uint32_t)g_rs64_last_guest_pc);
    }
}
'''
    t = t.replace(anchor, fn + anchor + "    rs64_s4213_census(task);\n")
    rsp.write_text(t); print("patched")
