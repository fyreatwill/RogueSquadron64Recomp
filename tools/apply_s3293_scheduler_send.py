#!/usr/bin/env python3
"""Inject s3293 spTaskSchedulerThread 0x8011A818-send census into funcs_4.c.

Sites: L_80019ED0 ($s2[0] gate that can skip the send), 0x80019EE0
(lbu 0x80128D44), 0x80019F1C (jal osSendMesg taken), and the
flag-zero skip to L_80019F24. Diagnostic only — no skip, allow,
restore, or wait bypass.

This patches an already-sentinel'd RecompiledFuncs/funcs_4.c without
re-running the full fixup. The same transform lives in
../N64Recomp/fixup_game_funcs.py for the next clear+regen+fixup.
"""
from pathlib import Path

GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c")
MARK = "PATCH: s3293 scheduler send"

HELPER = r'''
static void rs64_s3293_scheduler_send(const char* site, uint32_t a0, uint32_t a1,
                                      uint32_t a2, uint32_t flag, uint32_t s2b0) {
    static unsigned long n_ed0 = 0, n_ee0 = 0, n_f1c = 0, n_f24 = 0;
    unsigned long *np;
    unsigned long n;
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    if (site[3] == 'D') np = &n_ed0;
    else if (site[3] == 'E') np = &n_ee0;
    else if (site[4] == '1') np = &n_f1c;
    else np = &n_f24;
    n = ++*np;
    {
        uint32_t width = rs64_vi_committed_width();
        if (width < 640u && n > 10ul && (n % 50ul) != 0ul) return;
        fprintf(stderr,
                "[s3293-sched] site=%s n=%lu a0=0x%08X a1=0x%08X a2=0x%08X flag28D44=0x%02X s2b0=0x%02X phase=%u width=%u origin=0x%06X\n",
                site, n, a0, a1, a2, flag & 0xFFu, s2b0 & 0xFFu,
                rs64_phase_ord(), width,
                rs64_vi_committed_origin() & 0x00FFFFFFu);
    }
    fflush(stderr);
}
'''

DECL_ANCHOR = '#include "funcs.h"\n'

ED0_OLD = (
    "L_80019ED0:\n"
    "    // 0x80019ED0: lbu         $v0, 0x0($s2)\n"
    "    ctx->r2 = MEM_BU(ctx->r18, 0X0);\n"
)
ED0_NEW = (
    "L_80019ED0:\n"
    "    // 0x80019ED0: lbu         $v0, 0x0($s2)\n"
    "    ctx->r2 = MEM_BU(ctx->r18, 0X0);\n"
    "    { /* PATCH: s3293 scheduler send */\n"
    "        rs64_s3293_scheduler_send(\"19ED0\", U32(ctx->r4), U32(ctx->r5), U32(ctx->r6),\n"
    "                                  (uint32_t)MEM_BU(-0X72BC, 0x80130000u), U32(ctx->r2));\n"
    "    }\n"
)

EE0_OLD = (
    "    // 0x80019EE0: lbu         $v0, -0x72BC($v0)\n"
    "    ctx->r2 = MEM_BU(ctx->r2, -0X72BC);\n"
)
EE0_NEW = (
    "    // 0x80019EE0: lbu         $v0, -0x72BC($v0)\n"
    "    ctx->r2 = MEM_BU(ctx->r2, -0X72BC);\n"
    "    { /* PATCH: s3293 scheduler send */\n"
    "        rs64_s3293_scheduler_send(\"19EE0\", U32(ctx->r4), U32(ctx->r5), U32(ctx->r6),\n"
    "                                  U32(ctx->r2), (uint32_t)MEM_BU(0X0, ctx->r18));\n"
    "    }\n"
)

F24_OLD = (
    "    // 0x80019EE4: beq         $v0, $zero, L_80019F24\n"
    "    if (ctx->r2 == 0) {\n"
    "        // 0x80019EE8: nop\n"
    "    \n"
    "            goto L_80019F24;\n"
    "    }\n"
)
F24_NEW = (
    "    // 0x80019EE4: beq         $v0, $zero, L_80019F24\n"
    "    if (ctx->r2 == 0) {\n"
    "        // 0x80019EE8: nop\n"
    "    \n"
    "            { /* PATCH: s3293 scheduler send */\n"
    "                rs64_s3293_scheduler_send(\"19F24\", U32(ctx->r4), U32(ctx->r5), U32(ctx->r6),\n"
    "                                          U32(ctx->r2), (uint32_t)MEM_BU(0X0, ctx->r18));\n"
    "            }\n"
    "            goto L_80019F24;\n"
    "    }\n"
)

SEND_OLD = (
    "    // 0x80019F1C: jal         0x80033410\n"
    "    // 0x80019F20: addu        $a2, $zero, $zero\n"
    "    ctx->r6 = ADD32(0, 0);\n"
    "    osSendMesg_recomp(rdram, ctx);\n"
)
SEND_NEW = (
    "    // 0x80019F1C: jal         0x80033410\n"
    "    // 0x80019F20: addu        $a2, $zero, $zero\n"
    "    ctx->r6 = ADD32(0, 0);\n"
    "    { /* PATCH: s3293 scheduler send */\n"
    "        rs64_s3293_scheduler_send(\"19F1C\", U32(ctx->r4), U32(ctx->r5), U32(ctx->r6),\n"
    "                                  (uint32_t)MEM_BU(-0X72BC, 0x80130000u), (uint32_t)MEM_BU(0X0, ctx->r18));\n"
    "    }\n"
    "    osSendMesg_recomp(rdram, ctx);\n"
)


def apply_s3293_scheduler_send_text(text: str):
    if MARK in text:
        return text, ["funcs_4.c: s3293 scheduler send already present"], False
    replacements = (
        (DECL_ANCHOR, DECL_ANCHOR + HELPER + "\n"),
        (ED0_OLD, ED0_NEW),
        (EE0_OLD, EE0_NEW),
        (F24_OLD, F24_NEW),
        (SEND_OLD, SEND_NEW),
    )
    for old, new in replacements:
        n = text.count(old)
        if n != 1:
            raise RuntimeError(f"s3293 anchor count={n} for {old[:80]!r}")
        text = text.replace(old, new, 1)
    return text, ["funcs_4.c: s3293 scheduler send probe patched x4"], True


def main():
    text, msgs, changed = apply_s3293_scheduler_send_text(GEN.read_text())
    for m in msgs:
        print(m)
    if changed:
        GEN.write_text(text)
        print(f"patched {GEN}")


if __name__ == "__main__":
    main()
