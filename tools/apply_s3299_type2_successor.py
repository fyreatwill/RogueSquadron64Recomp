#!/usr/bin/env python3
"""Inject s3299 spTaskSchedulerThread type-2 successor census into funcs_4.c.

Sites: L_80019D90 (type-2 entry), 0x80019D94 busy-skip, 0x80019DAC
(osSpTaskYield), 0x80019DC0 (sw msg+4 into 0x80128D40), and
L_80019DCC (idle start). Keep s3288 fade / s3289 SENT / s3290 inner
/ s3293 gate / s3294 loop / s3295 dispatch probes. Diagnostic only —
no skip, allow, restore, or wait bypass.

This patches an already-sentinel'd RecompiledFuncs/funcs_4.c without
re-running the full fixup. The same transform lives in
../N64Recomp/fixup_game_funcs.py for the next clear+regen+fixup.
"""
from pathlib import Path

GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c")
MARK = "PATCH: s3299 type2 successor"

HELPER = r'''
static void rs64_s3299_type2_successor(const char* site, int idx, uint32_t a0,
                                       uint32_t v0, uint32_t s3, uint32_t s2b0,
                                       uint32_t yieldw, uint32_t sp89c) {
    static unsigned long n[5];
    unsigned long c;
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    c = ++n[idx];
    {
        uint32_t width = rs64_vi_committed_width();
        if (width < 640u && c > 10ul && (c % 50ul) != 0ul) return;
        fprintf(stderr,
                "[s3299-t2] site=%s n=%lu a0=0x%08X v0=0x%08X s3=0x%08X s2b0=0x%02X yieldw=0x%08X sp89c=0x%02X phase=%u width=%u origin=0x%06X\n",
                site, c, a0, v0, s3, s2b0 & 0xFFu, yieldw, sp89c & 0xFFu,
                rs64_phase_ord(), width,
                rs64_vi_committed_origin() & 0x00FFFFFFu);
        if (idx == 0 && width >= 640u && (c % 50ul) == 0ul) {
            fprintf(stderr,
                    "[s3299-hist] n=%lu d90=%lu d94s=%lu dac=%lu dc0=%lu dcc=%lu phase=%u width=%u origin=0x%06X\n",
                    c, n[0], n[1], n[2], n[3], n[4],
                    rs64_phase_ord(), width,
                    rs64_vi_committed_origin() & 0x00FFFFFFu);
        }
    }
    fflush(stderr);
}
'''

DECL_ANCHOR = '#include "funcs.h"\n'

D90_OLD = (
    "L_80019D90:\n"
    "    // 0x80019D90: lbu         $v0, 0x0($s3)\n"
    "    ctx->r2 = MEM_BU(ctx->r19, 0X0);\n"
    "    // 0x80019D94: bne         $v0, $zero, L_80019CC4\n"
)
D90_NEW = (
    "L_80019D90:\n"
    "    // 0x80019D90: lbu         $v0, 0x0($s3)\n"
    "    ctx->r2 = MEM_BU(ctx->r19, 0X0);\n"
    "    { /* PATCH: s3299 type2 successor */\n"
    "        rs64_s3299_type2_successor(\"19D90\", 0, U32(ctx->r4), U32(ctx->r2),\n"
    "                                   U32(ctx->r19), (uint32_t)MEM_BU(0X0, ctx->r18),\n"
    "                                   U32(MEM_W(S32(0X8013 << 16), -0X72C0)),\n"
    "                                   (uint32_t)MEM_BU(ctx->r19, -0X4));\n"
    "    }\n"
    "    // 0x80019D94: bne         $v0, $zero, L_80019CC4\n"
)

D94S_OLD = (
    "    // 0x80019D94: bne         $v0, $zero, L_80019CC4\n"
    "    if (ctx->r2 != 0) {\n"
    "        // 0x80019D98: nop\n"
    "    \n"
    "            goto L_80019CC4;\n"
    "    }\n"
)
D94S_NEW = (
    "    // 0x80019D94: bne         $v0, $zero, L_80019CC4\n"
    "    if (ctx->r2 != 0) {\n"
    "        // 0x80019D98: nop\n"
    "    \n"
    "            { /* PATCH: s3299 type2 successor */\n"
    "                rs64_s3299_type2_successor(\"19D94S\", 1, U32(ctx->r4), U32(ctx->r2),\n"
    "                                           U32(ctx->r19), (uint32_t)MEM_BU(0X0, ctx->r18),\n"
    "                                           U32(MEM_W(S32(0X8013 << 16), -0X72C0)),\n"
    "                                           (uint32_t)MEM_BU(ctx->r19, -0X4));\n"
    "            }\n"
    "            goto L_80019CC4;\n"
    "    }\n"
)

DAC_OLD = (
    "    // 0x80019DAC: jal         0x80034430\n"
    "    // 0x80019DB0: nop\n"
    "\n"
    "    osSpTaskYield_recomp(rdram, ctx);\n"
)
DAC_NEW = (
    "    // 0x80019DAC: jal         0x80034430\n"
    "    // 0x80019DB0: nop\n"
    "\n"
    "    { /* PATCH: s3299 type2 successor */\n"
    "        rs64_s3299_type2_successor(\"19DAC\", 2, U32(ctx->r4), U32(ctx->r2),\n"
    "                                   U32(ctx->r19), (uint32_t)MEM_BU(0X0, ctx->r18),\n"
    "                                   U32(MEM_W(S32(0X8013 << 16), -0X72C0)),\n"
    "                                   (uint32_t)MEM_BU(ctx->r19, -0X4));\n"
    "    }\n"
    "    osSpTaskYield_recomp(rdram, ctx);\n"
)

DC0_OLD = (
    "    rs64_probe_submit_gate_store('W', 0x80019DC0u, U32(ADD32(ctx->r1, -0X72C0)), U32(ctx->r2));\n"
    "    MEM_W(-0X72C0, ctx->r1) = ctx->r2;\n"
    "    // 0x80019DC4: j           L_80019CC4\n"
)
DC0_NEW = (
    "    rs64_probe_submit_gate_store('W', 0x80019DC0u, U32(ADD32(ctx->r1, -0X72C0)), U32(ctx->r2));\n"
    "    MEM_W(-0X72C0, ctx->r1) = ctx->r2;\n"
    "    { /* PATCH: s3299 type2 successor */\n"
    "        rs64_s3299_type2_successor(\"19DC0\", 3, U32(ctx->r4), U32(ctx->r2),\n"
    "                                   U32(ctx->r19), (uint32_t)MEM_BU(0X0, ctx->r18),\n"
    "                                   U32(ctx->r2),\n"
    "                                   (uint32_t)MEM_BU(ctx->r19, -0X4));\n"
    "    }\n"
    "    // 0x80019DC4: j           L_80019CC4\n"
)

DCC_OLD = (
    "L_80019DCC:\n"
    "    // 0x80019DCC: lui         $at, 0x8012\n"
    "    ctx->r1 = S32(0X8012 << 16);\n"
)
DCC_NEW = (
    "L_80019DCC:\n"
    "    // 0x80019DCC: lui         $at, 0x8012\n"
    "    ctx->r1 = S32(0X8012 << 16);\n"
    "    { /* PATCH: s3299 type2 successor */\n"
    "        rs64_s3299_type2_successor(\"19DCC\", 4, U32(ctx->r4), U32(ctx->r2),\n"
    "                                   U32(ctx->r19), (uint32_t)MEM_BU(0X0, ctx->r18),\n"
    "                                   U32(MEM_W(S32(0X8013 << 16), -0X72C0)),\n"
    "                                   (uint32_t)MEM_BU(ctx->r19, -0X4));\n"
    "    }\n"
)


def apply_s3299_type2_successor_text(text: str):
    if MARK in text:
        return text, ["funcs_4.c: s3299 type2 successor already present"], False
    replacements = (
        (DECL_ANCHOR, DECL_ANCHOR + HELPER + "\n"),
        (D90_OLD, D90_NEW),
        (D94S_OLD, D94S_NEW),
        (DAC_OLD, DAC_NEW),
        (DC0_OLD, DC0_NEW),
        (DCC_OLD, DCC_NEW),
    )
    for old, new in replacements:
        n = text.count(old)
        if n != 1:
            raise RuntimeError(f"s3299 anchor count={n} for {old[:80]!r}")
        text = text.replace(old, new, 1)
    return text, ["funcs_4.c: s3299 type2 successor probe patched x5"], True


def main():
    text, msgs, changed = apply_s3299_type2_successor_text(GEN.read_text())
    for m in msgs:
        print(m)
    if changed:
        GEN.write_text(text)
        print(f"patched {GEN}")


if __name__ == "__main__":
    main()
