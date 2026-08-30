#!/usr/bin/env python3
"""Inject s3295 spTaskSchedulerThread recv-dispatch census into funcs_4.c.

Sites: 0x80019CDC type-byte load, L_80019DFC, L_80019E7C, and
0x80019E80 taken vs fallthrough. Keep s3288 fade / s3289 SENT /
s3290 inner / s3293 gate / s3294 loop probes. Diagnostic only —
no skip, allow, restore, or wait bypass.

This patches an already-sentinel'd RecompiledFuncs/funcs_4.c without
re-running the full fixup. The same transform lives in
../N64Recomp/fixup_game_funcs.py for the next clear+regen+fixup.
"""
from pathlib import Path

GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c")
MARK = "PATCH: s3295 scheduler dispatch"

HELPER = r'''
static void rs64_s3295_scheduler_dispatch(const char* site, int idx, uint32_t a0,
                                          uint32_t typ, uint32_t s1, uint32_t s5,
                                          uint32_t s2b0, uint32_t yieldw) {
    static unsigned long n[5];
    static unsigned long type_n[256];
    unsigned long c;
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    c = ++n[idx];
    if (idx == 0) {
        type_n[typ & 0xFFu]++;
    }
    {
        uint32_t width = rs64_vi_committed_width();
        if (width < 640u && c > 10ul && (c % 50ul) != 0ul) return;
        fprintf(stderr,
                "[s3295-disp] site=%s n=%lu type=0x%02X is81=%d a0=0x%08X s1=0x%02X s5=0x%02X s2b0=0x%02X yieldw=0x%08X phase=%u width=%u origin=0x%06X\n",
                site, c, typ & 0xFFu, (typ & 0xFFu) == 0x81u ? 1 : 0, a0,
                s1 & 0xFFu, s5 & 0xFFu, s2b0 & 0xFFu, yieldw,
                rs64_phase_ord(), width,
                rs64_vi_committed_origin() & 0x00FFFFFFu);
        if (idx == 0 && width >= 640u && ((c % 50ul) == 0ul || (typ & 0xFFu) == 0x81u)) {
            unsigned long i, other = 0;
            for (i = 0; i < 256ul; ++i) {
                if (i != 0ul && i != 1ul && i != 2ul && i != 0x81ul) other += type_n[i];
            }
            fprintf(stderr,
                    "[s3295-hist] n=%lu t00=%lu t01=%lu t02=%lu t81=%lu other=%lu phase=%u width=%u origin=0x%06X\n",
                    c, type_n[0], type_n[1], type_n[2], type_n[0x81], other,
                    rs64_phase_ord(), width,
                    rs64_vi_committed_origin() & 0x00FFFFFFu);
        }
    }
    fflush(stderr);
}
'''

DECL_ANCHOR = '#include "funcs.h"\n'

CDC_OLD = (
    "    // 0x80019CDC: lbu         $v1, 0x0($a0)\n"
    "    ctx->r3 = MEM_BU(ctx->r4, 0X0);\n"
    "    // 0x80019CE0: beq         $v1, $s5, L_80019D90\n"
)
CDC_NEW = (
    "    // 0x80019CDC: lbu         $v1, 0x0($a0)\n"
    "    ctx->r3 = MEM_BU(ctx->r4, 0X0);\n"
    "    { /* PATCH: s3295 scheduler dispatch */\n"
    "        rs64_s3295_scheduler_dispatch(\"19CDC\", 0, U32(ctx->r4), U32(ctx->r3),\n"
    "                                      U32(ctx->r17), U32(ctx->r21),\n"
    "                                      (uint32_t)MEM_BU(0X0, ctx->r18),\n"
    "                                      U32(MEM_W(S32(0X8013 << 16), -0X72C0)));\n"
    "    }\n"
    "    // 0x80019CE0: beq         $v1, $s5, L_80019D90\n"
)

DFC_OLD = (
    "L_80019DFC:\n"
    "    // 0x80019DFC: lui         $v0, 0x8013\n"
    "    ctx->r2 = S32(0X8013 << 16);\n"
    "    // 0x80019E00: lw          $v0, -0x72C0($v0)\n"
    "    ctx->r2 = MEM_W(ctx->r2, -0X72C0);\n"
    "    // 0x80019E04: beq         $v0, $zero, L_80019E7C\n"
)
DFC_NEW = (
    "L_80019DFC:\n"
    "    // 0x80019DFC: lui         $v0, 0x8013\n"
    "    ctx->r2 = S32(0X8013 << 16);\n"
    "    // 0x80019E00: lw          $v0, -0x72C0($v0)\n"
    "    ctx->r2 = MEM_W(ctx->r2, -0X72C0);\n"
    "    { /* PATCH: s3295 scheduler dispatch */\n"
    "        rs64_s3295_scheduler_dispatch(\"19DFC\", 1, U32(ctx->r4), U32(ctx->r3),\n"
    "                                      U32(ctx->r17), U32(ctx->r21),\n"
    "                                      (uint32_t)MEM_BU(0X0, ctx->r18),\n"
    "                                      U32(ctx->r2));\n"
    "    }\n"
    "    // 0x80019E04: beq         $v0, $zero, L_80019E7C\n"
)

E7C_OLD = (
    "L_80019E7C:\n"
    "    // 0x80019E7C: lbu         $v0, 0x0($s2)\n"
    "    ctx->r2 = MEM_BU(ctx->r18, 0X0);\n"
    "    // 0x80019E80: bne         $v0, $s1, L_80019ED0\n"
    "    if (ctx->r2 != ctx->r17) {\n"
    "        // 0x80019E84: addu        $a1, $zero, $zero\n"
    "        ctx->r5 = ADD32(0, 0);\n"
    "            goto L_80019ED0;\n"
    "    }\n"
    "    // 0x80019E84: addu        $a1, $zero, $zero\n"
    "    ctx->r5 = ADD32(0, 0);\n"
)
E7C_NEW = (
    "L_80019E7C:\n"
    "    // 0x80019E7C: lbu         $v0, 0x0($s2)\n"
    "    ctx->r2 = MEM_BU(ctx->r18, 0X0);\n"
    "    { /* PATCH: s3295 scheduler dispatch */\n"
    "        rs64_s3295_scheduler_dispatch(\"19E7C\", 2, U32(ctx->r4), U32(ctx->r3),\n"
    "                                      U32(ctx->r17), U32(ctx->r21),\n"
    "                                      U32(ctx->r2),\n"
    "                                      U32(MEM_W(S32(0X8013 << 16), -0X72C0)));\n"
    "    }\n"
    "    // 0x80019E80: bne         $v0, $s1, L_80019ED0\n"
    "    if (ctx->r2 != ctx->r17) {\n"
    "        // 0x80019E84: addu        $a1, $zero, $zero\n"
    "        ctx->r5 = ADD32(0, 0);\n"
    "        { /* PATCH: s3295 scheduler dispatch */\n"
    "            rs64_s3295_scheduler_dispatch(\"19E80T\", 3, U32(ctx->r4), U32(ctx->r3),\n"
    "                                          U32(ctx->r17), U32(ctx->r21),\n"
    "                                          U32(ctx->r2),\n"
    "                                          U32(MEM_W(S32(0X8013 << 16), -0X72C0)));\n"
    "        }\n"
    "            goto L_80019ED0;\n"
    "    }\n"
    "    { /* PATCH: s3295 scheduler dispatch */\n"
    "        rs64_s3295_scheduler_dispatch(\"19E80F\", 4, U32(ctx->r4), U32(ctx->r3),\n"
    "                                      U32(ctx->r17), U32(ctx->r21),\n"
    "                                      U32(ctx->r2),\n"
    "                                      U32(MEM_W(S32(0X8013 << 16), -0X72C0)));\n"
    "    }\n"
    "    // 0x80019E84: addu        $a1, $zero, $zero\n"
    "    ctx->r5 = ADD32(0, 0);\n"
)


def apply_s3295_scheduler_dispatch_text(text: str):
    if MARK in text:
        return text, ["funcs_4.c: s3295 scheduler dispatch already present"], False
    replacements = (
        (DECL_ANCHOR, DECL_ANCHOR + HELPER + "\n"),
        (CDC_OLD, CDC_NEW),
        (DFC_OLD, DFC_NEW),
        (E7C_OLD, E7C_NEW),
    )
    for old, new in replacements:
        n = text.count(old)
        if n != 1:
            raise RuntimeError(f"s3295 anchor count={n} for {old[:80]!r}")
        text = text.replace(old, new, 1)
    return text, ["funcs_4.c: s3295 scheduler dispatch probe patched x4"], True


def main():
    text, msgs, changed = apply_s3295_scheduler_dispatch_text(GEN.read_text())
    for m in msgs:
        print(m)
    if changed:
        GEN.write_text(text)
        print(f"patched {GEN}")


if __name__ == "__main__":
    main()
