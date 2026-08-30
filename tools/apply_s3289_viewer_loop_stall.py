#!/usr/bin/env python3
"""Inject s3289 runMenuModelViewerScreen loop-stall census into funcs_33.c.

Sites: L_800C29E0, L_800C2A40, and entry+return of the six 2D50-fallthrough
callees. Keep the s3288 fade census. Diagnostic only — no skip, allow,
restore, or wait bypass.

This patches an already-sentinel'd RecompiledFuncs/funcs_33.c without
re-running the full fixup. The same transform lives in
../N64Recomp/fixup_game_funcs.py for the next clear+regen+fixup.
"""
from pathlib import Path

GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_33.c")
MARK = "PATCH: s3289 viewer stall"

HELPER = r'''
static void rs64_s3289_viewer_stall(const char* site, uint32_t s2, uint32_t s5) {
    static unsigned long n_29e0 = 0, n_2a40 = 0;
    static unsigned long n_went = 0, n_wret = 0;
    static unsigned long n_rent = 0, n_rret = 0;
    static unsigned long n_bent = 0, n_bret = 0;
    static unsigned long n_cent = 0, n_cret = 0;
    static unsigned long n_dent = 0, n_dret = 0;
    static unsigned long n_sent = 0, n_sret = 0;
    static const char* open_site = "";
    static unsigned long open_n = 0;
    unsigned long *np;
    unsigned long n;
    int is_ent;
    int is_ret;
    int miss;
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    is_ent = (site[1] == 'E');
    is_ret = (site[1] == 'R');
    miss = 0;
    if (is_ret) {
        if (open_site[0] && open_site[0] == site[0]) {
            open_site = "";
            open_n = 0;
        } else if (open_site[0]) {
            miss = 1;
        }
    } else if (is_ent) {
        if (open_site[0]) miss = 1;
        open_site = site;
    } else if (open_site[0]) {
        miss = 1;
    }
    if (site[0] == '2' && site[1] == '9') np = &n_29e0;
    else if (site[0] == '2' && site[1] == 'A') np = &n_2a40;
    else if (site[0] == 'W' && site[1] == 'E') np = &n_went;
    else if (site[0] == 'W' && site[1] == 'R') np = &n_wret;
    else if (site[0] == 'R' && site[1] == 'E') np = &n_rent;
    else if (site[0] == 'R' && site[1] == 'R') np = &n_rret;
    else if (site[0] == 'B' && site[1] == 'E') np = &n_bent;
    else if (site[0] == 'B' && site[1] == 'R') np = &n_bret;
    else if (site[0] == 'C' && site[1] == 'E') np = &n_cent;
    else if (site[0] == 'C' && site[1] == 'R') np = &n_cret;
    else if (site[0] == 'D' && site[1] == 'E') np = &n_dent;
    else if (site[0] == 'D' && site[1] == 'R') np = &n_dret;
    else if (site[0] == 'S' && site[1] == 'E') np = &n_sent;
    else np = &n_sret;
    n = ++*np;
    if (is_ent) open_n = n;
    if (!miss && n > 10ul && (n % 50ul) != 0ul) return;
    fprintf(stderr,
            "[s3289-stall] site=%s n=%lu open=%s open_n=%lu miss=%d s2=0x%08X s5=0x%08X phase=%u width=%u origin=0x%06X\n",
            site, n, open_site[0] ? open_site : "-", open_n, miss, s2, s5,
            rs64_phase_ord(), rs64_vi_committed_width(),
            rs64_vi_committed_origin() & 0x00FFFFFFu);
    fflush(stderr);
}
'''

HELPER_ANCHOR = (
    '            "[s3288-fade] site=%s n=%lu taken_n=%lu c1cs=%d s2=0x%08X s5=0x%08X f24=0x%08X taken=%d phase=%u width=%u origin=0x%06X\\n",\n'
    "            site, n, n_2d50_taken, c1cs, s2, s5, f24, taken,\n"
    "            rs64_phase_ord(), rs64_vi_committed_width(),\n"
    "            rs64_vi_committed_origin() & 0x00FFFFFFu);\n"
    "    fflush(stderr);\n"
    "}\n"
)

LOOP_HEAD_OLD = (
    "L_800C29E0:\n"
    "    // 0x800C29E0: jal         0x800C6660\n"
)
LOOP_HEAD_NEW = (
    "L_800C29E0:\n"
    "    { /* PATCH: s3289 viewer stall */\n"
    "        rs64_s3289_viewer_stall(\"29E0\", U32(ctx->r18), U32(ctx->r21));\n"
    "    }\n"
    "    // 0x800C29E0: jal         0x800C6660\n"
)

A40_OLD = (
    "L_800C2A40:\n"
    "    // 0x800C2A40: add.s       $f24, $f24, $f0\n"
)
A40_NEW = (
    "L_800C2A40:\n"
    "    { /* PATCH: s3289 viewer stall */\n"
    "        rs64_s3289_viewer_stall(\"2A40\", U32(ctx->r18), U32(ctx->r21));\n"
    "    }\n"
    "    // 0x800C2A40: add.s       $f24, $f24, $f0\n"
)

WAIT_ENT_OLD = (
    "    // 0x800C2D58: jal         0x8000A86C\n"
    "    // 0x800C2D5C: nop\n"
    "\n"
    "    waitForPrevFrameDone(rdram, ctx);\n"
    "        goto after_22;\n"
)
WAIT_ENT_NEW = (
    "    // 0x800C2D58: jal         0x8000A86C\n"
    "    // 0x800C2D5C: nop\n"
    "\n"
    "    { /* PATCH: s3289 viewer stall */\n"
    "        rs64_s3289_viewer_stall(\"WENT\", U32(ctx->r18), U32(ctx->r21));\n"
    "    }\n"
    "    waitForPrevFrameDone(rdram, ctx);\n"
    "        goto after_22;\n"
)

WAIT_RET_OLD = (
    "        goto after_22;\n"
    "    // 0x800C2D5C: nop\n"
    "\n"
    "    after_22:\n"
    "    // 0x800C2D60: jal         0x8000A6CC\n"
)
WAIT_RET_NEW = (
    "        goto after_22;\n"
    "    // 0x800C2D5C: nop\n"
    "\n"
    "    after_22:\n"
    "    { /* PATCH: s3289 viewer stall */\n"
    "        rs64_s3289_viewer_stall(\"WRET\", U32(ctx->r18), U32(ctx->r21));\n"
    "    }\n"
    "    // 0x800C2D60: jal         0x8000A6CC\n"
)

RESET_ENT_OLD = (
    "    // 0x800C2D60: jal         0x8000A6CC\n"
    "    // 0x800C2D64: nop\n"
    "\n"
    "    frameStartReset(rdram, ctx);\n"
    "        goto after_23;\n"
)
RESET_ENT_NEW = (
    "    // 0x800C2D60: jal         0x8000A6CC\n"
    "    // 0x800C2D64: nop\n"
    "\n"
    "    { /* PATCH: s3289 viewer stall */\n"
    "        rs64_s3289_viewer_stall(\"RENT\", U32(ctx->r18), U32(ctx->r21));\n"
    "    }\n"
    "    frameStartReset(rdram, ctx);\n"
    "        goto after_23;\n"
)

RESET_RET_OLD = (
    "        goto after_23;\n"
    "    // 0x800C2D64: nop\n"
    "\n"
    "    after_23:\n"
    "    // 0x800C2D68: lui         $v0, 0x800D\n"
)
RESET_RET_NEW = (
    "        goto after_23;\n"
    "    // 0x800C2D64: nop\n"
    "\n"
    "    after_23:\n"
    "    { /* PATCH: s3289 viewer stall */\n"
    "        rs64_s3289_viewer_stall(\"RRET\", U32(ctx->r18), U32(ctx->r21));\n"
    "    }\n"
    "    // 0x800C2D68: lui         $v0, 0x800D\n"
)

REBUILD_ENT_OLD = (
    "    // 0x800C2D70: jal         0x80064488\n"
    "    // 0x800C2D74: nop\n"
    "\n"
    "    rebuildActiveDisplayObjectList(rdram, ctx);\n"
    "        goto after_24;\n"
)
REBUILD_ENT_NEW = (
    "    // 0x800C2D70: jal         0x80064488\n"
    "    // 0x800C2D74: nop\n"
    "\n"
    "    { /* PATCH: s3289 viewer stall */\n"
    "        rs64_s3289_viewer_stall(\"BENT\", U32(ctx->r18), U32(ctx->r21));\n"
    "    }\n"
    "    rebuildActiveDisplayObjectList(rdram, ctx);\n"
    "        goto after_24;\n"
)

REBUILD_RET_OLD = (
    "        goto after_24;\n"
    "    // 0x800C2D74: nop\n"
    "\n"
    "    after_24:\n"
    "    // 0x800C2D78: addu        $a0, $s6, $zero\n"
)
REBUILD_RET_NEW = (
    "        goto after_24;\n"
    "    // 0x800C2D74: nop\n"
    "\n"
    "    after_24:\n"
    "    { /* PATCH: s3289 viewer stall */\n"
    "        rs64_s3289_viewer_stall(\"BRET\", U32(ctx->r18), U32(ctx->r21));\n"
    "    }\n"
    "    // 0x800C2D78: addu        $a0, $s6, $zero\n"
)

CAMERA_ENT_OLD = (
    '    rs64_m5_setup_caller_boundary("runMenuModelViewerScreen", 0x800C2D84u, ctx->r31, U32(ctx->r4), U32(ctx->r5)); /* PATCH: s2469 setup caller boundary */\n'
    "    setupCameraMatrices(rdram, ctx);\n"
    "        goto after_25;\n"
)
CAMERA_ENT_NEW = (
    '    rs64_m5_setup_caller_boundary("runMenuModelViewerScreen", 0x800C2D84u, ctx->r31, U32(ctx->r4), U32(ctx->r5)); /* PATCH: s2469 setup caller boundary */\n'
    "    { /* PATCH: s3289 viewer stall */\n"
    "        rs64_s3289_viewer_stall(\"CENT\", U32(ctx->r18), U32(ctx->r21));\n"
    "    }\n"
    "    setupCameraMatrices(rdram, ctx);\n"
    "        goto after_25;\n"
)

CAMERA_RET_OLD = (
    "    MEM_W(0XC, ctx->r22) = 0;\n"
    "    after_25:\n"
    "    // 0x800C2D88: jal         0x8000B6F4\n"
)
CAMERA_RET_NEW = (
    "    MEM_W(0XC, ctx->r22) = 0;\n"
    "    after_25:\n"
    "    { /* PATCH: s3289 viewer stall */\n"
    "        rs64_s3289_viewer_stall(\"CRET\", U32(ctx->r18), U32(ctx->r21));\n"
    "    }\n"
    "    // 0x800C2D88: jal         0x8000B6F4\n"
)

BARS_ENT_OLD = (
    "    // 0x800C2D88: jal         0x8000B6F4\n"
    "    // 0x800C2D8C: nop\n"
    "\n"
    "    drawFrameProfilerBars(rdram, ctx);\n"
    "        goto after_26;\n"
)
BARS_ENT_NEW = (
    "    // 0x800C2D88: jal         0x8000B6F4\n"
    "    // 0x800C2D8C: nop\n"
    "\n"
    "    { /* PATCH: s3289 viewer stall */\n"
    "        rs64_s3289_viewer_stall(\"DENT\", U32(ctx->r18), U32(ctx->r21));\n"
    "    }\n"
    "    drawFrameProfilerBars(rdram, ctx);\n"
    "        goto after_26;\n"
)

BARS_RET_OLD = (
    "        goto after_26;\n"
    "    // 0x800C2D8C: nop\n"
    "\n"
    "    after_26:\n"
    "    // 0x800C2D90: jal         0x8000C07C\n"
)
BARS_RET_NEW = (
    "        goto after_26;\n"
    "    // 0x800C2D8C: nop\n"
    "\n"
    "    after_26:\n"
    "    { /* PATCH: s3289 viewer stall */\n"
    "        rs64_s3289_viewer_stall(\"DRET\", U32(ctx->r18), U32(ctx->r21));\n"
    "    }\n"
    "    // 0x800C2D90: jal         0x8000C07C\n"
)

SUBMIT_ENT_OLD = (
    "    // 0x800C2D90: jal         0x8000C07C\n"
    "    // 0x800C2D94: nop\n"
    "\n"
    "    submitGfxFrame(rdram, ctx);\n"
    "        goto after_27;\n"
)
SUBMIT_ENT_NEW = (
    "    // 0x800C2D90: jal         0x8000C07C\n"
    "    // 0x800C2D94: nop\n"
    "\n"
    "    { /* PATCH: s3289 viewer stall */\n"
    "        rs64_s3289_viewer_stall(\"SENT\", U32(ctx->r18), U32(ctx->r21));\n"
    "    }\n"
    "    submitGfxFrame(rdram, ctx);\n"
    "        goto after_27;\n"
)

SUBMIT_RET_OLD = (
    "        goto after_27;\n"
    "    // 0x800C2D94: nop\n"
    "\n"
    "    after_27:\n"
    "    // 0x800C2D98: j           L_800C29E0\n"
)
SUBMIT_RET_NEW = (
    "        goto after_27;\n"
    "    // 0x800C2D94: nop\n"
    "\n"
    "    after_27:\n"
    "    { /* PATCH: s3289 viewer stall */\n"
    "        rs64_s3289_viewer_stall(\"SRET\", U32(ctx->r18), U32(ctx->r21));\n"
    "    }\n"
    "    // 0x800C2D98: j           L_800C29E0\n"
)


def apply_s3289_viewer_loop_stall_text(text: str):
    if MARK in text:
        return text, ["funcs_33.c: s3289 viewer stall already present"], False
    replacements = (
        (HELPER_ANCHOR, HELPER_ANCHOR + HELPER + "\n"),
        (LOOP_HEAD_OLD, LOOP_HEAD_NEW),
        (A40_OLD, A40_NEW),
        (WAIT_ENT_OLD, WAIT_ENT_NEW),
        (WAIT_RET_OLD, WAIT_RET_NEW),
        (RESET_ENT_OLD, RESET_ENT_NEW),
        (RESET_RET_OLD, RESET_RET_NEW),
        (REBUILD_ENT_OLD, REBUILD_ENT_NEW),
        (REBUILD_RET_OLD, REBUILD_RET_NEW),
        (CAMERA_ENT_OLD, CAMERA_ENT_NEW),
        (CAMERA_RET_OLD, CAMERA_RET_NEW),
        (BARS_ENT_OLD, BARS_ENT_NEW),
        (BARS_RET_OLD, BARS_RET_NEW),
        (SUBMIT_ENT_OLD, SUBMIT_ENT_NEW),
        (SUBMIT_RET_OLD, SUBMIT_RET_NEW),
    )
    for old, new in replacements:
        n = text.count(old)
        if n != 1:
            raise RuntimeError(f"s3289 anchor count={n} for {old[:80]!r}")
        text = text.replace(old, new, 1)
    return text, ["funcs_33.c: s3289 viewer stall probe patched x14"], True


def main():
    text, msgs, changed = apply_s3289_viewer_loop_stall_text(GEN.read_text())
    for m in msgs:
        print(m)
    if changed:
        GEN.write_text(text)
        print(f"patched {GEN}")


if __name__ == "__main__":
    main()
