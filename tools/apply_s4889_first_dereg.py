#!/usr/bin/env python3
"""Apply the bounded first gate-zero teardown deregistration experiment.

The origin is the named gate-zero teardown gap: the first reapply registers
the synth callback without the teardown's normal deregistration. The default
arm removes one already-present synth entry before that reapply; the rollback
arm leaves the generated path unchanged.
"""
from pathlib import Path

# s7476 class ED ORIGIN: findAndZeroTableSlotMatching (0x8000794C) uses $a1 as its slot loop index (and clobbers
# $v0/$v1). The original body saved only $a0, so when the synth entry sat in slot 1 initN64RspMixer received
# a1 = 1 instead of the scene's voice count (retail: 17 on the first scene, oracle s7476) -> a 1-voice MusyX
# array while voice[1] stays live (the s7475 overrun). The call now preserves $a1/$v0/$v1 too.
# ROGUESQ_S7476_A1FIX=0 restores the old clobber (A/B arm only).
CALL = ("uint32_t saved_r4 = U32(ctx->r4), s7476_r5 = U32(ctx->r5), s7476_r2 = U32(ctx->r2), s7476_r3 = U32(ctx->r3); "
        "ctx->r4 = S32(0x8009123Cu); findAndZeroTableSlotMatching(rdram, ctx); ctx->r4 = saved_r4; "
        "{ static int s7476_fx = -1; if (s7476_fx < 0) { const char* e7 = getenv(\"ROGUESQ_S7476_A1FIX\"); s7476_fx = !(e7 && e7[0] == 48); } "
        "fprintf(stderr, \"[s7476] dereg a1 before=%u after=%u fix=%d\\n\", (unsigned)s7476_r5, (unsigned)U32(ctx->r5), s7476_fx); "
        "if (s7476_fx) { ctx->r5 = S32(s7476_r5); ctx->r2 = S32(s7476_r2); ctx->r3 = S32(s7476_r3); } } s_done = 1; ")
OLD_CALL = ("uint32_t saved_r4 = U32(ctx->r4); ctx->r4 = S32(0x8009123Cu); "
            "findAndZeroTableSlotMatching(rdram, ctx); ctx->r4 = saved_r4; s_done = 1; ")
path = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
text = path.read_text()
marker = "PATCH: s4889 first gate-zero dereg"
if marker in text:
    if OLD_CALL in text:   # upgrade a pre-s7476 application in place
        text = text.replace(OLD_CALL, CALL, 1)
        path.write_text(text)
        print("upgraded (s7476 a1 preserve)")
    else:
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
    + CALL +
    "fprintf(stderr, \"[s4889] first-gate-zero-dereg ra=0x%08X\\n\", (unsigned)ctx->r31); } }\n"
)
text = text[:pos] + body + text[pos:]
path.write_text(text)
print("applied")
