#!/usr/bin/env python3
"""s4700: retrace callback-table (0x8011A8A4, 4 slots) trace, env ROGUESQ_LOG_S4700_CB=1. Idempotent; apply after the s4562 pause patch.
Logs (a) every registerSiCallback (0x80007910) call: a0 + table; (b) every findAndZeroTableSlotMatching (0x8000794C) call: a0, table
before, matched slot, table after; (c) musyxSynthFrame wrapper entries: every 200th (and every entry whose table lacks 0x8009123C)
with the table words, ra and pause state. ra==0x80019B7C means a table dispatch; anything else is a direct caller."""
from pathlib import Path
R = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
H = ('static int s_on = -1; if (s_on < 0) { const char* e = getenv("ROGUESQ_LOG_S4700_CB"); s_on = (e && e[0] && e[0] != 48) ? 1 : 0; } ')
T = ('(unsigned)MEM_W(0X0, (int32_t)0x8011A8A4), (unsigned)MEM_W(0X4, (int32_t)0x8011A8A4), '
     '(unsigned)MEM_W(0X8, (int32_t)0x8011A8A4), (unsigned)MEM_W(0XC, (int32_t)0x8011A8A4)')
f2 = R / "funcs_2.c"; s = f2.read_text(); M = "PATCH: s4700 cbtable"
if M not in s:
    a = 'RECOMP_FUNC void registerSiCallback(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n'
    assert s.count(a) == 1
    s = s.replace(a, a + '    { /* ' + M + ' */ ' + H + 'if (s_on) fprintf(stderr, "[s4700-cb] register a0=0x%08X ra=0x%08X tbl=%08X %08X %08X %08X\\n", (unsigned)ctx->r4, (unsigned)ctx->r31, ' + T + '); }\n', 1)
    b = 'RECOMP_FUNC void findAndZeroTableSlotMatching(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n'
    assert s.count(b) == 1
    s = s.replace(b, b + '    { /* ' + M + ' */ ' + H + 'if (s_on) fprintf(stderr, "[s4700-cb] dereg-enter a0=0x%08X ra=0x%08X tbl=%08X %08X %08X %08X\\n", (unsigned)ctx->r4, (unsigned)ctx->r31, ' + T + '); }\n', 1)
    c = 'L_80007978:\n    // 0x80007978: jr          $ra\n'
    assert s.count(c) == 1
    s = s.replace(c, 'L_80007978:\n    { /* ' + M + ' */ ' + H + 'if (s_on) fprintf(stderr, "[s4700-cb] dereg-exit a1(slots scanned)=%u tbl=%08X %08X %08X %08X\\n", (unsigned)ctx->r5, ' + T + '); }\n    // 0x80007978: jr          $ra\n', 1)
    f2.write_text(s)
f24 = R / "funcs_24.c"; t = f24.read_text()
if M not in t:
    d = 'RECOMP_FUNC void musyxSynthFrame(uint8_t* rdram, recomp_context* ctx) {\n'
    assert t.count(d) == 1
    t = t.replace(d, d + '    { /* ' + M + ' */ ' + H + 'if (s_on) { static unsigned s_n = 0; unsigned n = s_n++; int has = ((unsigned)MEM_W(0X0, (int32_t)0x8011A8A4) == 0x8009123Cu) || ((unsigned)MEM_W(0X4, (int32_t)0x8011A8A4) == 0x8009123Cu) || ((unsigned)MEM_W(0X8, (int32_t)0x8011A8A4) == 0x8009123Cu) || ((unsigned)MEM_W(0XC, (int32_t)0x8011A8A4) == 0x8009123Cu);\n'
        '      if ((n % 200) == 0 || !has) { static unsigned s_nh = 0; if (has || s_nh++ < 64) fprintf(stderr, "[s4700-cb] synth-enter n=%u has_entry=%d ra=0x%08X pause=%d head=%08X tbl=%08X %08X %08X %08X\\n", n, has, (unsigned)ctx->r31, g_s4562_pause, (unsigned)MEM_W(0X0, (int32_t)0x801499B0), ' + T + '); } } }\n', 1)
    f24.write_text(t)
# s4700b: host backtrace at every registerSiCallback with a0==0x8009123C (names the caller that registers the synth a 2nd time)
M2 = "PATCH: s4700 cbtable bt"
s = f2.read_text()
if M2 not in s:
    a = 'RECOMP_FUNC void registerSiCallback(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n'
    assert s.count(a) == 1
    s = s.replace(a, a + '    { /* ' + M2 + ' */ extern int backtrace(void**, int); extern void backtrace_symbols_fd(void* const*, int, int); static int s_on2 = -1; if (s_on2 < 0) { const char* e = getenv("ROGUESQ_LOG_S4700_CB"); s_on2 = (e && e[0] && e[0] != 48) ? 1 : 0; }\n'
        '      if (s_on2 && (unsigned)ctx->r4 == 0x8009123Cu) { void* bt[24]; int n = backtrace(bt, 24); fprintf(stderr, "[s4700-cb] register-synth backtrace:\\n"); backtrace_symbols_fd(bt, n, 2); } }\n', 1)
    f2.write_text(s)
print("ok")
