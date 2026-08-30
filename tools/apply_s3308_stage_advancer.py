#!/usr/bin/env python3
"""Inject s3308 cinematicStageAdvancer producer-table probes into funcs_29.c.

Sites: entry 0x800AF550, ptr-check 0x800AF55C ($v1 at 0x800B0934),
fp compare 0x800AF590, stage<7 0x800AF5B4 (0x800B0938), $v0=1 jr
0x800AF5BC, $v0=0 jr L_800AF604. Diagnostic only — no skip, allow,
restore, or guest store/branch change.

This patches an already-sentinel'd RecompiledFuncs/funcs_29.c without
re-running the full fixup. The same transform is called from
../N64Recomp/fixup_game_funcs.py for the next clear+regen+fixup.
"""
from pathlib import Path


GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_29.c")
MARK = "PATCH: s3308 stage adv"

HELPER = r'''
/* PATCH: s3308 stage adv */
static void rs64_s3308_stage_adv(uint8_t* rdram, uint32_t edge_id,
                                 const char* site, uint32_t pc,
                                 uint32_t v0, uint32_t v1, uint32_t taken,
                                 uint32_t f0_bits, uint32_t f2_bits,
                                 uint32_t a2, uint32_t acc, uint32_t ra) {
    static int enabled = -1;
    static int marked = 0;
    static uint32_t last_width = 0xFFFFFFFFu;
    static unsigned long n[6];
    static unsigned long printed[6];
    unsigned long c;
    uint32_t width;
    uint32_t ptr;
    uint32_t stage;
    int always;
    if (enabled < 0) {
        const char* all = getenv("ROGUESQ_LOG_ALL");
        const char* own = getenv("ROGUESQ_LOG_M5_STAGE_ADV");
        const char* sib = getenv("ROGUESQ_LOG_M5_CINE_LOOP");
        enabled = ((all && all[0] && all[0] != '0') ||
                   (own && own[0] && own[0] != '0') ||
                   (sib && sib[0] && sib[0] != '0')) ? 1 : 0;
    }
    if (!enabled || edge_id >= 6u) return;
    if (!marked) {
        const char* mark = getenv("ROGUESQ_M5_STAGE_ADV_MARK_ALL");
        const char* mark2 = getenv("ROGUESQ_M5_CINE_LOOP_MARK_ALL");
        const char* mark3 = getenv("ROGUESQ_M5_POSTVIEWER_MARK_ALL");
        if ((mark && mark[0] && mark[0] != '0') ||
            (mark2 && mark2[0] && mark2[0] != '0') ||
            (mark3 && mark3[0] && mark3[0] != '0')) {
            uint32_t i;
            for (i = 0; i < 6u; i++) {
                fprintf(stderr, "[s3308-stage-adv-control] mark edge_id=%u\n", i);
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
        for (i = 0; i < 6u; i++) printed[i] = 0;
    }
    c = ++n[edge_id];
    always = (edge_id == 4u || taken != 0u);
    if (!always) {
        if (width < 640u) return;
        printed[edge_id]++;
        if (printed[edge_id] > 8ul && (c % 50ul) != 0ul) return;
    }
    ptr = MEM_W(0x800B0000u, 0x934u);
    stage = MEM_BU(0x800B0000u, 0x938u);
    fprintf(stderr,
            "[s3308-stage-adv] phase=%u width=%u origin=0x%06X edge_id=%u site=%s pc=0x%08X v0=0x%08X v1=0x%08X taken=%u n=%lu ptr=0x%08X stage=%u acc=0x%02X f0=0x%08X f2=0x%08X a2=0x%08X ra=0x%08X\n",
            rs64_phase_ord(), width, rs64_vi_committed_origin() & 0x00FFFFFFu,
            edge_id, site, pc, v0, v1, taken, c, ptr, stage, acc,
            f0_bits, f2_bits, a2, ra);
    fflush(stderr);
}
'''

ENTRY_OLD = (
    "RECOMP_FUNC void cinematicStageAdvancer(uint8_t* rdram, recomp_context* ctx) {\n"
    "    uint64_t hi = 0, lo = 0, result = 0;\n"
    "    int c1cs = 0;\n"
    "    // 0x800AF550: lui         $v0, 0x800B\n"
)
ENTRY_NEW = (
    HELPER
    + "RECOMP_FUNC void cinematicStageAdvancer(uint8_t* rdram, recomp_context* ctx) {\n"
    "    uint64_t hi = 0, lo = 0, result = 0;\n"
    "    int c1cs = 0;\n"
    "    { /* PATCH: s3308 stage adv */\n"
    "        rs64_s3308_stage_adv(rdram, 0u, \"entry\", 0x800AF550u,\n"
    "                             U32(ctx->r2), U32(ctx->r3), 0u,\n"
    "                             ctx->f0.u32l, ctx->f2.u32l, U32(ctx->r6),\n"
    "                             0xFFu, U32(ctx->r31));\n"
    "    }\n"
    "    // 0x800AF550: lui         $v0, 0x800B\n"
)

PTR_OLD = (
    "    // 0x800AF55C: beq         $v1, $zero, L_800AF604\n"
    "    if (ctx->r3 == 0) {\n"
)
PTR_NEW = (
    "    { /* PATCH: s3308 stage adv */\n"
    "        rs64_s3308_stage_adv(rdram, 1u, \"ptr-check\", 0x800AF55Cu,\n"
    "                             U32(ctx->r2), U32(ctx->r3),\n"
    "                             (ctx->r3 == 0) ? 1u : 0u,\n"
    "                             ctx->f0.u32l, ctx->f2.u32l, U32(ctx->r6),\n"
    "                             0xFFu, U32(ctx->r31));\n"
    "    }\n"
    + PTR_OLD
)

CMP_OLD = (
    "    // 0x800AF590: bc1f        L_800AF5C4\n"
    "    if (!c1cs) {\n"
)
CMP_NEW = (
    "    { /* PATCH: s3308 stage adv */\n"
    "        rs64_s3308_stage_adv(rdram, 2u, \"fp-compare\", 0x800AF590u,\n"
    "                             U32(ctx->r2), U32(ctx->r3),\n"
    "                             c1cs ? 1u : 0u,\n"
    "                             ctx->f0.u32l, ctx->f2.u32l, U32(ctx->r6),\n"
    "                             (uint32_t)MEM_BU(ctx->r3, 0X2F), U32(ctx->r31));\n"
    "    }\n"
    + CMP_OLD
)

STAGE_OLD = (
    "    // 0x800AF5B0: sltiu       $v0, $v0, 0x7\n"
    "    ctx->r2 = ctx->r2 < 0X7 ? 1 : 0;\n"
    "    // 0x800AF5B4: bne         $v0, $zero, L_800AF604\n"
    "    if (ctx->r2 != 0) {\n"
)
STAGE_NEW = (
    "    // 0x800AF5B0: sltiu       $v0, $v0, 0x7\n"
    "    ctx->r2 = ctx->r2 < 0X7 ? 1 : 0;\n"
    "    { /* PATCH: s3308 stage adv */\n"
    "        rs64_s3308_stage_adv(rdram, 3u, \"stage-lt7\", 0x800AF5B4u,\n"
    "                             U32(ctx->r2), U32(ctx->r3),\n"
    "                             (ctx->r2 == 0) ? 1u : 0u,\n"
    "                             ctx->f0.u32l, ctx->f2.u32l, U32(ctx->r6),\n"
    "                             0xFFu, U32(ctx->r31));\n"
    "    }\n"
    "    // 0x800AF5B4: bne         $v0, $zero, L_800AF604\n"
    "    if (ctx->r2 != 0) {\n"
)

RET1_OLD = (
    "    // 0x800AF5B8: addiu       $v0, $zero, 0x1\n"
    "    ctx->r2 = ADD32(0, 0X1);\n"
    "    // 0x800AF5BC: jr          $ra\n"
    "    // 0x800AF5C0: nop\n"
    "\n"
    "    return;\n"
)
RET1_NEW = (
    "    // 0x800AF5B8: addiu       $v0, $zero, 0x1\n"
    "    ctx->r2 = ADD32(0, 0X1);\n"
    "    { /* PATCH: s3308 stage adv */\n"
    "        rs64_s3308_stage_adv(rdram, 4u, \"ret-one\", 0x800AF5BCu,\n"
    "                             U32(ctx->r2), U32(ctx->r3), 1u,\n"
    "                             ctx->f0.u32l, ctx->f2.u32l, U32(ctx->r6),\n"
    "                             0xFFu, U32(ctx->r31));\n"
    "    }\n"
    "    // 0x800AF5BC: jr          $ra\n"
    "    // 0x800AF5C0: nop\n"
    "\n"
    "    return;\n"
)

RET0_OLD = (
    "L_800AF604:\n"
    "    // 0x800AF604: jr          $ra\n"
    "    // 0x800AF608: addu        $v0, $zero, $zero\n"
    "    ctx->r2 = ADD32(0, 0);\n"
    "    return;\n"
)
RET0_NEW = (
    "L_800AF604:\n"
    "    // 0x800AF604: jr          $ra\n"
    "    // 0x800AF608: addu        $v0, $zero, $zero\n"
    "    ctx->r2 = ADD32(0, 0);\n"
    "    { /* PATCH: s3308 stage adv */\n"
    "        rs64_s3308_stage_adv(rdram, 5u, \"ret-zero\", 0x800AF604u,\n"
    "                             U32(ctx->r2), U32(ctx->r3), 0u,\n"
    "                             ctx->f0.u32l, ctx->f2.u32l, U32(ctx->r6),\n"
    "                             0xFFu, U32(ctx->r31));\n"
    "    }\n"
    "    return;\n"
)


def apply_s3308_stage_advancer_text(text):
    if MARK in text:
        return text, ["funcs_29.c: s3308 stage adv already present"], False
    replacements = (
        (ENTRY_OLD, ENTRY_NEW),
        (PTR_OLD, PTR_NEW),
        (CMP_OLD, CMP_NEW),
        (STAGE_OLD, STAGE_NEW),
        (RET1_OLD, RET1_NEW),
        (RET0_OLD, RET0_NEW),
    )
    for old, new in replacements:
        n = text.count(old)
        if n != 1:
            raise RuntimeError(f"s3308 anchor count={n} for {old[:80]!r}")
        text = text.replace(old, new, 1)
    return text, ["funcs_29.c: s3308 stage advancer probe patched x6"], True


def main():
    text, msgs, changed = apply_s3308_stage_advancer_text(GEN.read_text())
    for msg in msgs:
        print(msg)
    if changed:
        GEN.write_text(text)
        print(f"patched {GEN}")


if __name__ == "__main__":
    main()
