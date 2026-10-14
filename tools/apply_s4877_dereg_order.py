#!/usr/bin/env python3
"""s4877: names the caller of the port's synth dereg and its order vs reapplyAudioConfig. Env ROGUESQ_LOG_S4700_CB=1.
Rows: [s4877] enter <fn> ra=..; host backtrace at every findAndZeroTableSlotMatching(a0==0x8009123C). Idempotent; apply after apply_s4700_cbtable_trace.py."""
from pathlib import Path
R = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
H = ('static int s_on = -1; if (s_on < 0) { const char* e = getenv("ROGUESQ_LOG_S4700_CB"); s_on = (e && e[0] && e[0] != 48) ? 1 : 0; } ')
M = "PATCH: s4877 dereg order"
def enter(fn, addr):
    return ('    { /* ' + M + ' ' + fn + ' */ ' + H + 'if (s_on) fprintf(stderr, "[s4877] enter ' + fn + ' pc=' + addr + ' ra=0x%08X lastpc=0x%08X gate0F50=%u\\n", (unsigned)ctx->r31, (unsigned)g_rs64_last_guest_pc, (unsigned)MEM_BU(S32(0x800A << 16), 0xF50)); }\n')
for fname, fn, addr, hdr in [
    ("funcs_24.c", "reapplyAudioConfig", "0x80091C88", 'RECOMP_FUNC void reapplyAudioConfig(uint8_t* rdram, recomp_context* ctx) {\n'),
    ("funcs_24.c", "waitForMusyXAudioTaskDone", "0x80091EB0", 'RECOMP_FUNC void waitForMusyXAudioTaskDone(uint8_t* rdram, recomp_context* ctx) {\n'),
    ("funcs_23.c", "musyxNoopStub", "stub", 'RECOMP_FUNC void musyxNoopStub(uint8_t* rdram, recomp_context* ctx) {\n'),
    ("funcs_2.c", "findAndZeroTableSlotMatching", "0x8000794C", 'RECOMP_FUNC void findAndZeroTableSlotMatching(uint8_t* rdram, recomp_context* ctx) {\n'),
]:
    p = R / fname
    s = p.read_text()
    if (M + " " + fn) in s:
        continue
    assert s.count(hdr) == 1, (fn, s.count(hdr))
    body = enter(fn, addr)
    if fn == "findAndZeroTableSlotMatching":
        body += ('    { /* ' + M + ' bt */ extern int backtrace(void**, int); extern void backtrace_symbols_fd(void* const*, int, int); ' + H +
                 'if (s_on && (unsigned)ctx->r4 == 0x8009123Cu) { void* bt[16]; int n = backtrace(bt, 16); fprintf(stderr, "[s4877] dereg-synth backtrace:\\n"); backtrace_symbols_fd(bt, n, 2); } }\n')
    s = s.replace(hdr, hdr + body, 1)
    p.write_text(s)
print("ok")
