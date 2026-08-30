#!/usr/bin/env python3
"""Inject s3311 cinematicLoopBody initializer-jal skip probes into funcs_27.c.

Sites: time-pred beq 0x800A626C (sltu of 0xB28($s3) vs limit-10),
$a0-byte beq 0x800A6274, isCinematicActive bne 0x800A6288,
jal cinematicInitializer 0x800A62B4. Diagnostic only — no skip, allow,
restore, or guest store/branch change.

This patches an already-sentinel'd RecompiledFuncs/funcs_27.c without
re-running the full fixup. The same transform is called from
../N64Recomp/fixup_game_funcs.py for the next clear+regen+fixup.
"""
from pathlib import Path


GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c")
MARK = "PATCH: s3311 cine init jal"

HELPER = r'''
/* PATCH: s3311 cine init jal */
static void rs64_s3311_cine_init_jal(uint8_t* rdram, uint32_t edge_id,
                                     const char* site, uint32_t pc,
                                     uint32_t v0, uint32_t v1, uint32_t a0,
                                     uint32_t taken, uint32_t count,
                                     uint32_t limit, uint32_t ra) {
    static int enabled = -1;
    static int marked = 0;
    static uint32_t last_width = 0xFFFFFFFFu;
    static unsigned long n[4];
    static unsigned long printed[4];
    unsigned long c;
    uint32_t width;
    int always;
    (void)rdram;
    if (enabled < 0) {
        const char* all = getenv("ROGUESQ_LOG_ALL");
        const char* own = getenv("ROGUESQ_LOG_M5_CINE_INIT_JAL");
        const char* sib = getenv("ROGUESQ_LOG_M5_CINE_LOOP");
        const char* sib2 = getenv("ROGUESQ_LOG_M5_STAGE_ADV");
        enabled = ((all && all[0] && all[0] != '0') ||
                   (own && own[0] && own[0] != '0') ||
                   (sib && sib[0] && sib[0] != '0') ||
                   (sib2 && sib2[0] && sib2[0] != '0')) ? 1 : 0;
    }
    if (!enabled || edge_id >= 4u) return;
    if (!marked) {
        const char* mark = getenv("ROGUESQ_M5_CINE_INIT_JAL_MARK_ALL");
        const char* mark2 = getenv("ROGUESQ_M5_CINE_LOOP_MARK_ALL");
        const char* mark3 = getenv("ROGUESQ_M5_STAGE_ADV_MARK_ALL");
        const char* mark4 = getenv("ROGUESQ_M5_POSTVIEWER_MARK_ALL");
        if ((mark && mark[0] && mark[0] != '0') ||
            (mark2 && mark2[0] && mark2[0] != '0') ||
            (mark3 && mark3[0] && mark3[0] != '0') ||
            (mark4 && mark4[0] && mark4[0] != '0')) {
            uint32_t i;
            for (i = 0; i < 4u; i++) {
                fprintf(stderr, "[s3311-cine-init-jal-control] mark edge_id=%u\n", i);
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
        for (i = 0; i < 4u; i++) printed[i] = 0;
    }
    c = ++n[edge_id];
    always = (edge_id == 3u || taken != 0u);
    if (!always) {
        if (width < 640u) return;
        printed[edge_id]++;
        if (printed[edge_id] > 8ul && (c % 50ul) != 0ul) return;
    }
    fprintf(stderr,
            "[s3311-cine-init-jal] phase=%u width=%u origin=0x%06X edge_id=%u site=%s pc=0x%08X v0=0x%08X v1=0x%08X a0=0x%08X taken=%u n=%lu count=0x%08X limit=0x%08X ra=0x%08X\n",
            rs64_phase_ord(), width, rs64_vi_committed_origin() & 0x00FFFFFFu,
            edge_id, site, pc, v0, v1, a0, taken, c, count, limit, ra);
    fflush(stderr);
}

'''

DECL_OLD = (
    "RECOMP_FUNC void cinematicLoopBody(uint8_t* rdram, recomp_context* ctx) {\n"
)
DECL_NEW = HELPER + DECL_OLD

TIME_OLD = (
    "    // 0x800A626C: beq         $v1, $zero, L_800A627C\n"
    "    if (ctx->r3 == 0) {\n"
)
TIME_NEW = (
    "    { /* PATCH: s3311 cine init jal */\n"
    "        rs64_s3311_cine_init_jal(rdram, 0u, \"time-pred\", 0x800A626Cu,\n"
    "                                 U32(ctx->r2), U32(ctx->r3), U32(ctx->r4),\n"
    "                                 (ctx->r3 == 0) ? 1u : 0u,\n"
    "                                 U32(MEM_W(ctx->r19, 0xB28)), U32(ctx->r2),\n"
    "                                 U32(ctx->r31));\n"
    "    }\n"
    + TIME_OLD
)

FLAG_OLD = (
    "    // 0x800A6274: beq         $v0, $zero, L_800A62EC\n"
    "    if (ctx->r2 == 0) {\n"
)
FLAG_NEW = (
    "    { /* PATCH: s3311 cine init jal */\n"
    "        rs64_s3311_cine_init_jal(rdram, 1u, \"flag-byte\", 0x800A6274u,\n"
    "                                 U32(ctx->r2), U32(ctx->r3), U32(ctx->r4),\n"
    "                                 (ctx->r2 == 0) ? 1u : 0u,\n"
    "                                 U32(MEM_W(ctx->r19, 0xB28)), U32(ctx->r2),\n"
    "                                 U32(ctx->r31));\n"
    "    }\n"
    + FLAG_OLD
)

ACTIVE_OLD = (
    "    // 0x800A6288: bne         $v0, $zero, L_800A62EC\n"
    "    if (ctx->r2 != 0) {\n"
)
ACTIVE_NEW = (
    "    { /* PATCH: s3311 cine init jal */\n"
    "        rs64_s3311_cine_init_jal(rdram, 2u, \"already-active\", 0x800A6288u,\n"
    "                                 U32(ctx->r2), U32(ctx->r3), U32(ctx->r4),\n"
    "                                 (ctx->r2 != 0) ? 1u : 0u,\n"
    "                                 U32(MEM_W(ctx->r19, 0xB28)), U32(0),\n"
    "                                 U32(ctx->r31));\n"
    "    }\n"
    + ACTIVE_OLD
)

JAL_OLD = (
    "    // 0x800A62B4: jal         0x800AF408\n"
    "    // 0x800A62B8: addiu       $a1, $sp, 0x18\n"
    "    ctx->r5 = ADD32(ctx->r29, 0X18);\n"
    "    cinematicInitializer(rdram, ctx);\n"
)
JAL_NEW = (
    "    { /* PATCH: s3311 cine init jal */\n"
    "        rs64_s3311_cine_init_jal(rdram, 3u, \"init-jal\", 0x800A62B4u,\n"
    "                                 U32(ctx->r2), U32(ctx->r3), U32(ctx->r4),\n"
    "                                 1u,\n"
    "                                 U32(MEM_W(ctx->r19, 0xB28)), U32(ctx->r6),\n"
    "                                 U32(ctx->r31));\n"
    "    }\n"
    + JAL_OLD
)


def apply_s3311_cine_init_jal_text(text):
    if MARK in text:
        return text, ["funcs_27.c: s3311 cine init jal already present"], False
    replacements = (
        (DECL_OLD, DECL_NEW),
        (TIME_OLD, TIME_NEW),
        (FLAG_OLD, FLAG_NEW),
        (ACTIVE_OLD, ACTIVE_NEW),
        (JAL_OLD, JAL_NEW),
    )
    for old, new in replacements:
        n = text.count(old)
        if n != 1:
            raise RuntimeError(f"s3311 anchor count={n} for {old[:80]!r}")
        text = text.replace(old, new, 1)
    return text, ["funcs_27.c: s3311 cine init jal probe patched x4"], True


def main():
    text, msgs, changed = apply_s3311_cine_init_jal_text(GEN.read_text())
    for msg in msgs:
        print(msg)
    if changed:
        GEN.write_text(text)
        print(f"patched {GEN}")


if __name__ == "__main__":
    main()
