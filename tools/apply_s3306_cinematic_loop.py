#!/usr/bin/env python3
"""Inject s3306 cinematicLoopBody loop/exit edge probes into funcs_27.c.

Sites: 0x800A5DD8 ($v0), L_800A6024, 0x800A6074 ($v0), 0x800A64B4,
L_800A64BC, L_800A65E4, 0x800A6618. Keep the existing s3305
entry/return probes. Diagnostic only — no skip, allow, restore,
or guest store/branch change.

This patches an already-sentinel'd RecompiledFuncs/funcs_27.c without
re-running the full fixup. The same transform is called from
../N64Recomp/fixup_game_funcs.py for the next clear+regen+fixup.
"""
from pathlib import Path


GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c")
MARK = "PATCH: s3306 cine loop"

HELPER = r'''
/* PATCH: s3306 cine loop */
static void rs64_s3306_cine_loop(uint8_t* rdram, uint32_t edge_id,
                                 const char* site, uint32_t pc,
                                 uint32_t v0, uint32_t ra) {
    static int enabled = -1;
    static int marked = 0;
    static uint32_t last_width = 0xFFFFFFFFu;
    static unsigned long n[7];
    static unsigned long printed[7];
    static unsigned long v0_nz;
    unsigned long c;
    uint32_t width;
    uint32_t taken;
    int always;
    if (enabled < 0) {
        const char* all = getenv("ROGUESQ_LOG_ALL");
        const char* own = getenv("ROGUESQ_LOG_M5_CINE_LOOP");
        const char* sib = getenv("ROGUESQ_LOG_M5_POSTVIEWER_EDGE");
        enabled = ((all && all[0] && all[0] != '0') ||
                   (own && own[0] && own[0] != '0') ||
                   (sib && sib[0] && sib[0] != '0')) ? 1 : 0;
    }
    if (!enabled || edge_id >= 7u) return;
    if (!marked) {
        const char* mark = getenv("ROGUESQ_M5_CINE_LOOP_MARK_ALL");
        const char* mark2 = getenv("ROGUESQ_M5_POSTVIEWER_MARK_ALL");
        if ((mark && mark[0] && mark[0] != '0') ||
            (mark2 && mark2[0] && mark2[0] != '0')) {
            uint32_t i;
            for (i = 0; i < 7u; i++) {
                fprintf(stderr, "[s3306-cine-loop-control] mark edge_id=%u\n", i);
            }
            fflush(stderr);
        }
        marked = 1;
    }
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    width = rs64_vi_committed_width();
    if (width != last_width) {
        uint32_t i;
        last_width = width;
        for (i = 0; i < 7u; i++) printed[i] = 0;
    }
    c = ++n[edge_id];
    if (edge_id == 2u && v0 != 0u) ++v0_nz;
    taken = 0u;
    if (edge_id == 0u) taken = (v0 == 0u) ? 1u : 0u;
    else if (edge_id == 2u) taken = (v0 != 0u) ? 1u : 0u;
    always = (edge_id == 0u || edge_id == 4u || edge_id == 5u ||
              edge_id == 6u || taken != 0u);
    if (!always) {
        if (width < 640u) return;
        printed[edge_id]++;
        if (printed[edge_id] > 8ul && (c % 50ul) != 0ul) return;
    }
    fprintf(stderr,
            "[s3306-cine-loop] phase=%u width=%u origin=0x%06X edge_id=%u site=%s pc=0x%08X v0=0x%08X taken=%u n=%lu v0_nz=%lu ra=0x%08X\n",
            rs64_phase_ord(), width, rs64_vi_committed_origin() & 0x00FFFFFFu,
            edge_id, site, pc, v0, taken, c, v0_nz, ra);
    fflush(stderr);
}
'''

DECL_ANCHOR = '#include "funcs.h"\n'

EARLY_OLD = (
    "    // 0x800A5DD8: beq         $v0, $zero, L_800A65E4\n"
    "    if (ctx->r2 == 0) {\n"
)
EARLY_NEW = (
    "    { /* PATCH: s3306 cine loop */\n"
    "        rs64_s3306_cine_loop(rdram, 0u, \"early-exit\", 0x800A5DD8u,\n"
    "                             U32(ctx->r2), U32(ctx->r31));\n"
    "    }\n"
    + EARLY_OLD
)

HEAD_OLD = (
    "L_800A6024:\n"
    "    // 0x800A6024: jal         0x800AF360\n"
)
HEAD_NEW = (
    "L_800A6024:\n"
    "    { /* PATCH: s3306 cine loop */\n"
    "        rs64_s3306_cine_loop(rdram, 1u, \"loop-head\", 0x800A6024u,\n"
    "                             U32(ctx->r2), U32(ctx->r31));\n"
    "    }\n"
    "    // 0x800A6024: jal         0x800AF360\n"
)

GATE_OLD = (
    "    // 0x800A6074: bne         $v0, $zero, L_800A64BC\n"
    "    if (ctx->r2 != 0) {\n"
)
GATE_NEW = (
    "    { /* PATCH: s3306 cine loop */\n"
    "        rs64_s3306_cine_loop(rdram, 2u, \"exit-gate\", 0x800A6074u,\n"
    "                             U32(ctx->r2), U32(ctx->r31));\n"
    "    }\n"
    + GATE_OLD
)

BACK_OLD = (
    "    // 0x800A64B4: j           L_800A6024\n"
    "    // 0x800A64B8: nop\n"
    "\n"
    "        goto L_800A6024;\n"
)
BACK_NEW = (
    "    { /* PATCH: s3306 cine loop */\n"
    "        rs64_s3306_cine_loop(rdram, 3u, \"backedge\", 0x800A64B4u,\n"
    "                             U32(ctx->r2), U32(ctx->r31));\n"
    "    }\n"
    + BACK_OLD
)

TARGET_OLD = (
    "L_800A64BC:\n"
    "    // 0x800A64BC: jal         0x8000BF60\n"
)
TARGET_NEW = (
    "L_800A64BC:\n"
    "    { /* PATCH: s3306 cine loop */\n"
    "        rs64_s3306_cine_loop(rdram, 4u, \"exit-target\", 0x800A64BCu,\n"
    "                             U32(ctx->r2), U32(ctx->r31));\n"
    "    }\n"
    "    // 0x800A64BC: jal         0x8000BF60\n"
)

EPI_OLD = (
    "L_800A65E4:\n"
    "    // 0x800A65E4: lw          $ra, 0xBC($sp)\n"
)
EPI_NEW = (
    "L_800A65E4:\n"
    "    { /* PATCH: s3306 cine loop */\n"
    "        rs64_s3306_cine_loop(rdram, 5u, \"epilogue\", 0x800A65E4u,\n"
    "                             U32(ctx->r2), U32(ctx->r31));\n"
    "    }\n"
    "    // 0x800A65E4: lw          $ra, 0xBC($sp)\n"
)

RET_OLD = (
    "    // 0x800A6618: jr          $ra\n"
    "    // 0x800A661C: addiu       $sp, $sp, 0xD8\n"
)
RET_NEW = (
    "    { /* PATCH: s3306 cine loop */\n"
    "        rs64_s3306_cine_loop(rdram, 6u, \"cinematic-return\", 0x800A6618u,\n"
    "                             U32(ctx->r2), U32(ctx->r31));\n"
    "    }\n"
    + RET_OLD
)


def apply_s3306_cinematic_loop_text(text):
    if MARK in text:
        return text, ["funcs_27.c: s3306 cine loop already present"], False
    replacements = (
        (DECL_ANCHOR, DECL_ANCHOR + HELPER + "\n"),
        (EARLY_OLD, EARLY_NEW),
        (HEAD_OLD, HEAD_NEW),
        (GATE_OLD, GATE_NEW),
        (BACK_OLD, BACK_NEW),
        (TARGET_OLD, TARGET_NEW),
        (EPI_OLD, EPI_NEW),
        (RET_OLD, RET_NEW),
    )
    for old, new in replacements:
        n = text.count(old)
        if n != 1:
            raise RuntimeError(f"s3306 anchor count={n} for {old[:80]!r}")
        text = text.replace(old, new, 1)
    return text, ["funcs_27.c: s3306 cine loop probe patched x7"], True


def main():
    text, msgs, changed = apply_s3306_cinematic_loop_text(GEN.read_text())
    for msg in msgs:
        print(msg)
    if changed:
        GEN.write_text(text)
        print(f"patched {GEN}")


if __name__ == "__main__":
    main()
