#!/usr/bin/env python3
"""s4546: ROGUESQ_FL_ZERO_ALWAYS=1 makes the fl-zero mprotect page-fault watch hold
want=2 (page armed, busy re-arm) regardless of header shape, and run the
to_zero_correlate + fault_ring dump on any to_zero. Used with
ROGUESQ_LOG_FL_ZERO_WATCH=1 ROGUESQ_FL_ZERO_ADDR=0x1F9CD0 to name the writer that zeroes the
sample-heap block header word at 0x801F9CD4 (0x1800 -> 0). Diagnostic only. Idempotent."""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "src/main/main.cpp"
s = p.read_text()
if "flz_always" in s:
    print("already applied")
    raise SystemExit(0)


def rep(a, b):
    global s
    assert s.count(a) == 1, (a, s.count(a))
    s = s.replace(a, b, 1)


rep("""        uint8_t prev[16];
        snap16(prev);
        fprintf(stderr,
            "[fl-zero-poll] n=0 event=arm""", """        const bool flz_always = [] {
            const char* e = std::getenv("ROGUESQ_FL_ZERO_ALWAYS");
            return e && *e && *e != '0';
        }();
        uint8_t prev[16];
        snap16(prev);
        fprintf(stderr,
            "[fl-zero-poll] n=0 event=arm""")
rep("""        uint64_t n_change = 0;
        uint64_t n_poll = 0;
        uint64_t n_to_zero = 0;""", """#ifndef _WIN32
        if (flz_always) {
            g_flz_fault_want.store(2, std::memory_order_release);
            fl_zero_fault_arm();
            fprintf(stderr, "[fl-zero-fault] event=arm_always slot=0x%X\\n", slot);
            fflush(stderr);
        }
#endif
        uint64_t n_change = 0;
        uint64_t n_poll = 0;
        uint64_t n_to_zero = 0;""")
rep("""                if (cf == 0x2u && csz == 0x60u) {
                    if (g_flz_fault_want""", """                if ((cf == 0x2u && csz == 0x60u) || (flz_always && kind[0] != 't')) {
                    if (g_flz_fault_want""")
rep("if (kind[0] == 't' && pf == 0x2u && psz == 0x60u) {",
    "if (kind[0] == 't' && ((pf == 0x2u && psz == 0x60u) || flz_always)) {")
rep("if ((cf == 0x2u && csz == 0x60u) || (cf == 0 && csz == 0)) {\n                    fl_zero_fault_arm();",
    "if ((cf == 0x2u && csz == 0x60u) || (cf == 0 && csz == 0) || flz_always) {\n                    fl_zero_fault_arm();")
p.write_text(s)
print("applied")
