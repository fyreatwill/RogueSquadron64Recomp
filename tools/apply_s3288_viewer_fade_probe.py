#!/usr/bin/env python3
"""Inject s3288 runMenuModelViewerScreen fade-out census into funcs_33.c.

Sites: L_800C2B00, 0x800C2B84 (c1cs / $s5 / $s2 / $f24), 0x800C2D50 both
arms, L_800C2DA0, and the existing 0x800C2E00 return. Diagnostic only —
no skip, allow, restore, or wait bypass.

This patches an already-sentinel'd RecompiledFuncs/funcs_33.c without
re-running the full fixup. The same transform lives in
../N64Recomp/fixup_game_funcs.py for the next clear+regen+fixup.
"""
from pathlib import Path

GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_33.c")
MARK = "PATCH: s3288 viewer fade"

HELPER = r'''
static void rs64_s3288_viewer_fade(const char* site, int c1cs, uint32_t s2,
                                   uint32_t s5, uint32_t f24, int taken) {
    static unsigned long n_2b00 = 0, n_2b84 = 0, n_2d50 = 0, n_2d50_taken = 0;
    static unsigned long n_2da0 = 0, n_ret = 0;
    unsigned long *np;
    unsigned long n;
    int always;
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    if (site[0] == '2' && site[1] == 'B' && site[2] == '0') np = &n_2b00;
    else if (site[0] == '2' && site[1] == 'B' && site[2] == '8') np = &n_2b84;
    else if (site[0] == '2' && site[1] == 'D' && site[2] == '5') np = &n_2d50;
    else if (site[0] == '2' && site[1] == 'D' && site[2] == 'A') np = &n_2da0;
    else np = &n_ret;
    n = ++*np;
    if (taken && np == &n_2d50) ++n_2d50_taken;
    always = (np == &n_2da0 || np == &n_ret || (np == &n_2d50 && taken));
    if (!always && n > 10ul && (n % 50ul) != 0ul) return;
    fprintf(stderr,
            "[s3288-fade] site=%s n=%lu taken_n=%lu c1cs=%d s2=0x%08X s5=0x%08X f24=0x%08X taken=%d phase=%u width=%u origin=0x%06X\n",
            site, n, n_2d50_taken, c1cs, s2, s5, f24, taken,
            rs64_phase_ord(), rs64_vi_committed_width(),
            rs64_vi_committed_origin() & 0x00FFFFFFu);
    fflush(stderr);
}
'''

DECL_ANCHOR = (
    '#include "funcs.h"\n'
    '/* PATCH: s2045 m5 postwait declaration */\n'
    'extern void rs64_s2045_m5_postwait(uint8_t* rdram, uint32_t kind, const char* edge, const char* site, uint32_t pc, uint32_t a, uint32_t b, uint32_t c, uint32_t branch, uint32_t ra);\n'
)

B00_OLD = (
    "L_800C2B00:\n"
    "    // 0x800C2B00: sub.s       $f24, $f24, $f0\n"
)
B00_NEW = (
    "L_800C2B00:\n"
    "    { /* PATCH: s3288 viewer fade */\n"
    "        rs64_s3288_viewer_fade(\"2B00\", c1cs, U32(ctx->r18), U32(ctx->r21),\n"
    "                               ctx->f24.u32l, 0);\n"
    "    }\n"
    "    // 0x800C2B00: sub.s       $f24, $f24, $f0\n"
)

B84_OLD = (
    "    // 0x800C2B84: bc1tl       L_800C2B8C\n"
    "    if (c1cs) {\n"
    "        // 0x800C2B88: addiu       $s5, $zero, 0x1\n"
)
B84_NEW = (
    "    // 0x800C2B84: bc1tl       L_800C2B8C\n"
    "    { /* PATCH: s3288 viewer fade */\n"
    "        rs64_s3288_viewer_fade(\"2B84\", c1cs, U32(ctx->r18), U32(ctx->r21),\n"
    "                               ctx->f24.u32l, c1cs ? 1 : 0);\n"
    "    }\n"
    "    if (c1cs) {\n"
    "        // 0x800C2B88: addiu       $s5, $zero, 0x1\n"
)

D50_OLD = (
    "L_800C2D50:\n"
    "    // 0x800C2D50: beq         $s5, $v0, L_800C2DA0\n"
    "    if (ctx->r21 == ctx->r2) {\n"
)
D50_NEW = (
    "L_800C2D50:\n"
    "    // 0x800C2D50: beq         $s5, $v0, L_800C2DA0\n"
    "    { /* PATCH: s3288 viewer fade */\n"
    "        int s3288_taken = (ctx->r21 == ctx->r2) ? 1 : 0;\n"
    "        rs64_s3288_viewer_fade(\"2D50\", c1cs, U32(ctx->r18), U32(ctx->r21),\n"
    "                               ctx->f24.u32l, s3288_taken);\n"
    "    }\n"
    "    if (ctx->r21 == ctx->r2) {\n"
)

DA0_OLD = (
    "L_800C2DA0:\n"
    "    // 0x800C2DA0: jal         0x8000BF60\n"
)
DA0_NEW = (
    "L_800C2DA0:\n"
    "    { /* PATCH: s3288 viewer fade */\n"
    "        rs64_s3288_viewer_fade(\"2DA0\", c1cs, U32(ctx->r18), U32(ctx->r21),\n"
    "                               ctx->f24.u32l, 1);\n"
    "    }\n"
    "    // 0x800C2DA0: jal         0x8000BF60\n"
)

RET_OLD = (
    "    { // PATCH: s2045 runMenuModelViewerScreen return\n"
    "        rs64_s2045_m5_postwait(rdram, 10u, \"return\", \"runMenuModelViewerScreen\", 0x800C2E00u,\n"
)
RET_NEW = (
    "    { /* PATCH: s3288 viewer fade */\n"
    "        rs64_s3288_viewer_fade(\"return\", c1cs, U32(ctx->r18), U32(ctx->r21),\n"
    "                               ctx->f24.u32l, 1);\n"
    "    }\n"
    "    { // PATCH: s2045 runMenuModelViewerScreen return\n"
    "        rs64_s2045_m5_postwait(rdram, 10u, \"return\", \"runMenuModelViewerScreen\", 0x800C2E00u,\n"
)


def apply_s3288_viewer_fade_probe_text(text: str):
    if MARK in text:
        return text, ["funcs_33.c: s3288 viewer fade already present"], False
    replacements = (
        (DECL_ANCHOR, DECL_ANCHOR + HELPER + "\n"),
        (B00_OLD, B00_NEW),
        (B84_OLD, B84_NEW),
        (D50_OLD, D50_NEW),
        (DA0_OLD, DA0_NEW),
        (RET_OLD, RET_NEW),
    )
    for old, new in replacements:
        n = text.count(old)
        if n != 1:
            raise RuntimeError(f"s3288 anchor count={n} for {old[:60]!r}")
        text = text.replace(old, new, 1)
    return text, ["funcs_33.c: s3288 viewer fade probe patched x5"], True


def main():
    text, msgs, changed = apply_s3288_viewer_fade_probe_text(GEN.read_text())
    for m in msgs:
        print(m)
    if changed:
        GEN.write_text(text)
        print(f"patched {GEN}")


if __name__ == "__main__":
    main()
