#!/usr/bin/env python3
"""Inject s3294 spTaskSchedulerThread stall census into funcs_4.c.

Sites: L_80019CC4 (loop head), 0x80019CD0 recv entry+return, and
0x80019F64 ($s2[0]!=0 send to 0x8011A800) entry+return. Keep the
s3293 19ED0/19F1C census. Diagnostic only — no skip, allow, restore,
or wait bypass.

This patches an already-sentinel'd RecompiledFuncs/funcs_4.c without
re-running the full fixup. The same transform lives in
../N64Recomp/fixup_game_funcs.py for the next clear+regen+fixup.
"""
from pathlib import Path

GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c")
MARK = "PATCH: s3294 scheduler stall"

HELPER = r'''
static void rs64_s3294_scheduler_stall(const char* site, int idx, uint32_t a0,
                                       uint32_t a1, uint32_t a2, uint32_t s2b0) {
    static unsigned long n[5];
    static const char* open = "";
    static unsigned long open_n = 0;
    unsigned long c;
    int miss;
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    c = ++n[idx];
    miss = 0;
    if (idx == 1 || idx == 3) {
        if (open[0]) miss = 1;
        open = site;
        open_n = c;
    } else if (idx == 2 || idx == 4) {
        if (open[0] && open[1] == site[1] && open[2] == site[2] &&
            open[3] == site[3] && open[4] == site[4]) {
            open = "";
            open_n = 0;
        } else if (open[0]) {
            miss = 1;
        }
    }
    {
        uint32_t width = rs64_vi_committed_width();
        if (!miss && width < 640u && c > 10ul && (c % 50ul) != 0ul) return;
        fprintf(stderr,
                "[s3294-stall] site=%s n=%lu open=%s open_n=%lu miss=%d a0=0x%08X a1=0x%08X a2=0x%08X s2b0=0x%02X phase=%u width=%u origin=0x%06X\n",
                site, c, open[0] ? open : "-", open_n, miss, a0, a1, a2, s2b0 & 0xFFu,
                rs64_phase_ord(), width,
                rs64_vi_committed_origin() & 0x00FFFFFFu);
    }
    fflush(stderr);
}
'''

DECL_ANCHOR = '#include "funcs.h"\n'

CC4_OLD = (
    "L_80019CC4:\n"
    "    // 0x80019CC4: lui         $a0, 0x8012\n"
    "    ctx->r4 = S32(0X8012 << 16);\n"
    "    // 0x80019CC8: addiu       $a0, $a0, -0x5BE0\n"
    "    ctx->r4 = ADD32(ctx->r4, -0X5BE0);\n"
    "    // 0x80019CCC: addiu       $a1, $sp, 0x10\n"
    "    ctx->r5 = ADD32(ctx->r29, 0X10);\n"
)
CC4_NEW = (
    "L_80019CC4:\n"
    "    // 0x80019CC4: lui         $a0, 0x8012\n"
    "    ctx->r4 = S32(0X8012 << 16);\n"
    "    // 0x80019CC8: addiu       $a0, $a0, -0x5BE0\n"
    "    ctx->r4 = ADD32(ctx->r4, -0X5BE0);\n"
    "    // 0x80019CCC: addiu       $a1, $sp, 0x10\n"
    "    ctx->r5 = ADD32(ctx->r29, 0X10);\n"
    "    { /* PATCH: s3294 scheduler stall */\n"
    "        rs64_s3294_scheduler_stall(\"19CC4\", 0, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6),\n"
    "                                   (uint32_t)MEM_BU(0X0, ctx->r18));\n"
    "    }\n"
)

CD0E_OLD = (
    "    // 0x80019CD0: jal         0x800331D0\n"
    "    // 0x80019CD4: addiu       $a2, $zero, 0x1\n"
    "    ctx->r6 = ADD32(0, 0X1);\n"
    "    osRecvMesg_recomp(rdram, ctx);\n"
)
CD0E_NEW = (
    "    // 0x80019CD0: jal         0x800331D0\n"
    "    // 0x80019CD4: addiu       $a2, $zero, 0x1\n"
    "    ctx->r6 = ADD32(0, 0X1);\n"
    "    { /* PATCH: s3294 scheduler stall */\n"
    "        rs64_s3294_scheduler_stall(\"E0CD0\", 1, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6),\n"
    "                                   (uint32_t)MEM_BU(0X0, ctx->r18));\n"
    "    }\n"
    "    osRecvMesg_recomp(rdram, ctx);\n"
)

CD0R_OLD = (
    "    after_4:\n"
    "    rs64_m5_scheduler_recv_identity(rdram, 0x80019CD0u, U32(ctx->r31), U32(ADD32(ctx->r29, 0x10)), U32(ctx->r2)); /* PATCH: s3256 scheduler recv identity */\n"
)
CD0R_NEW = (
    "    after_4:\n"
    "    { /* PATCH: s3294 scheduler stall */\n"
    "        rs64_s3294_scheduler_stall(\"R0CD0\", 2, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6),\n"
    "                                   (uint32_t)MEM_BU(0X0, ctx->r18));\n"
    "    }\n"
    "    rs64_m5_scheduler_recv_identity(rdram, 0x80019CD0u, U32(ctx->r31), U32(ADD32(ctx->r29, 0x10)), U32(ctx->r2)); /* PATCH: s3256 scheduler recv identity */\n"
)

F64E_OLD = (
    "    // 0x80019F64: jal         0x80033410\n"
    "    // 0x80019F68: nop\n"
    "\n"
    "    osSendMesg_recomp(rdram, ctx);\n"
)
F64E_NEW = (
    "    // 0x80019F64: jal         0x80033410\n"
    "    // 0x80019F68: nop\n"
    "\n"
    "    { /* PATCH: s3294 scheduler stall */\n"
    "        rs64_s3294_scheduler_stall(\"E0F64\", 3, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6),\n"
    "                                   (uint32_t)MEM_BU(0X0, ctx->r18));\n"
    "    }\n"
    "    osSendMesg_recomp(rdram, ctx);\n"
)

F64R_OLD = (
    "    after_20:\n"
    "    // 0x80019F6C: sb          $zero, 0x0($s2)\n"
)
F64R_NEW = (
    "    after_20:\n"
    "    { /* PATCH: s3294 scheduler stall */\n"
    "        rs64_s3294_scheduler_stall(\"R0F64\", 4, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6),\n"
    "                                   (uint32_t)MEM_BU(0X0, ctx->r18));\n"
    "    }\n"
    "    // 0x80019F6C: sb          $zero, 0x0($s2)\n"
)


def apply_s3294_scheduler_stall_text(text: str):
    if MARK in text:
        return text, ["funcs_4.c: s3294 scheduler stall already present"], False
    replacements = (
        (DECL_ANCHOR, DECL_ANCHOR + HELPER + "\n"),
        (CC4_OLD, CC4_NEW),
        (CD0E_OLD, CD0E_NEW),
        (CD0R_OLD, CD0R_NEW),
        (F64E_OLD, F64E_NEW),
        (F64R_OLD, F64R_NEW),
    )
    for old, new in replacements:
        n = text.count(old)
        if n != 1:
            raise RuntimeError(f"s3294 anchor count={n} for {old[:80]!r}")
        text = text.replace(old, new, 1)
    return text, ["funcs_4.c: s3294 scheduler stall probe patched x5"], True


def main():
    text, msgs, changed = apply_s3294_scheduler_stall_text(GEN.read_text())
    for m in msgs:
        print(m)
    if changed:
        GEN.write_text(text)
        print(f"patched {GEN}")


if __name__ == "__main__":
    main()
