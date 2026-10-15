#!/usr/bin/env python3
"""Apply the bounded first gate-zero teardown deregistration experiment.

The origin is the named gate-zero teardown gap: the first reapply registers
the synth callback without the teardown's normal deregistration. The default
arm removes one already-present synth entry before that reapply; the rollback
arm leaves the generated path unchanged.
"""
from pathlib import Path

path = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
text = path.read_text()
marker = "PATCH: s4889 first gate-zero dereg"
if marker in text:
    print("already applied")
    raise SystemExit(0)

anchor = "    initN64RspMixer(rdram, ctx);\n"
target = anchor
needle = "RECOMP_FUNC void reapplyAudioConfig(uint8_t* rdram, recomp_context* ctx) {"
start = text.index(needle)
pos = text.index(anchor, start)
body = (
    "    { /* " + marker + " */ static int s_on = -1; static int s_done = 0; "
    "if (s_on < 0) { const char* e = getenv(\"ROGUESQ_S4889_FIRST_DEREG\"); "
    "s_on = !(e && e[0] == 48); } "
    "if (s_on && !s_done && (unsigned)MEM_BU(S32(0x800A << 16), 0xF50) == 0 && "
    "((unsigned)MEM_W(0X0, (int32_t)0x8011A8A4) == 0x8009123Cu || "
    "(unsigned)MEM_W(0X4, (int32_t)0x8011A8A4) == 0x8009123Cu || "
    "(unsigned)MEM_W(0X8, (int32_t)0x8011A8A4) == 0x8009123Cu || "
    "(unsigned)MEM_W(0XC, (int32_t)0x8011A8A4) == 0x8009123Cu)) { "
    "uint32_t saved_r4 = U32(ctx->r4); ctx->r4 = S32(0x8009123Cu); "
    "findAndZeroTableSlotMatching(rdram, ctx); ctx->r4 = saved_r4; s_done = 1; "
    "fprintf(stderr, \"[s4889] first-gate-zero-dereg ra=0x%08X\\n\", (unsigned)ctx->r31); } }\n"
)
text = text[:pos] + body + text[pos:]
path.write_text(text)
print("applied")
