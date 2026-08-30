#!/usr/bin/env python3
"""Inject s3300 0x8011A89C writer census into funcs_4.c.

Sites: type-1 0x80019CF0 taken / L_80019D10 / type-1 osSpTaskLoad
0x80019D58 / type-1 busy L_80019D78 / idle-start store 0x80019DD4 /
clearer 0x80019FE4. Keep s3288 fade / s3289 SENT / s3290 inner /
s3293 gate / s3294 loop / s3295 dispatch / s3299 type-2 probes.
Diagnostic only — no skip, allow, restore, or wait bypass.

This patches an already-sentinel'd RecompiledFuncs/funcs_4.c without
re-running the full fixup. The same transform lives in
../N64Recomp/fixup_game_funcs.py for the next clear+regen+fixup.
"""
from pathlib import Path

GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c")
MARK = "PATCH: s3300 sp busy writer"

HELPER = r'''
static void rs64_s3300_sp_busy_writer(const char* site, int idx, uint32_t a0,
                                      uint32_t v0, uint32_t s4_0, uint32_t s4_4,
                                      uint32_t sp89c, uint32_t yieldw, uint32_t s2b0) {
    static unsigned long n[6];
    unsigned long c;
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    c = ++n[idx];
    {
        uint32_t width = rs64_vi_committed_width();
        if (width < 640u && c > 10ul && (c % 50ul) != 0ul) return;
        fprintf(stderr,
                "[s3300-89c] site=%s n=%lu a0=0x%08X v0=0x%08X s4_0=0x%02X s4_4=0x%02X sp89c=0x%02X yieldw=0x%08X s2b0=0x%02X phase=%u width=%u origin=0x%06X\n",
                site, c, a0, v0, s4_0 & 0xFFu, s4_4 & 0xFFu, sp89c & 0xFFu,
                yieldw, s2b0 & 0xFFu,
                rs64_phase_ord(), width,
                rs64_vi_committed_origin() & 0x00FFFFFFu);
        if (idx == 1 && width >= 640u && (c % 50ul) == 0ul) {
            fprintf(stderr,
                    "[s3300-hist] n=%lu cf0t=%lu d10=%lu d58=%lu d78=%lu dd4=%lu fe4=%lu phase=%u width=%u origin=0x%06X\n",
                    c, n[0], n[1], n[2], n[3], n[4], n[5],
                    rs64_phase_ord(), width,
                    rs64_vi_committed_origin() & 0x00FFFFFFu);
        }
    }
    fflush(stderr);
}
'''

DECL_ANCHOR = '#include "funcs.h"\n'

CF0T_OLD = (
    "    // 0x80019CF0: beq         $v1, $s1, L_80019D10\n"
    "    if (ctx->r3 == ctx->r17) {\n"
    "        // 0x80019CF4: nop\n"
    "    \n"
    "            goto L_80019D10;\n"
    "    }\n"
)
CF0T_NEW = (
    "    // 0x80019CF0: beq         $v1, $s1, L_80019D10\n"
    "    if (ctx->r3 == ctx->r17) {\n"
    "        // 0x80019CF4: nop\n"
    "    \n"
    "            { /* PATCH: s3300 sp busy writer */\n"
    "                rs64_s3300_sp_busy_writer(\"19CF0T\", 0, U32(ctx->r4), U32(ctx->r3),\n"
    "                                          (uint32_t)MEM_BU(ctx->r20, 0X0),\n"
    "                                          (uint32_t)MEM_BU(ctx->r20, 0X4),\n"
    "                                          (uint32_t)MEM_BU(ctx->r19, -0X4),\n"
    "                                          U32(MEM_W(S32(0X8013 << 16), -0X72C0)),\n"
    "                                          (uint32_t)MEM_BU(0X0, ctx->r18));\n"
    "            }\n"
    "            goto L_80019D10;\n"
    "    }\n"
)

D10_OLD = (
    "L_80019D10:\n"
    "    // 0x80019D10: lbu         $v0, 0x0($s4)\n"
    "    ctx->r2 = MEM_BU(ctx->r20, 0X0);\n"
    "    // 0x80019D14: bne         $v0, $zero, L_80019D78\n"
)
D10_NEW = (
    "L_80019D10:\n"
    "    // 0x80019D10: lbu         $v0, 0x0($s4)\n"
    "    ctx->r2 = MEM_BU(ctx->r20, 0X0);\n"
    "    { /* PATCH: s3300 sp busy writer */\n"
    "        rs64_s3300_sp_busy_writer(\"19D10\", 1, U32(ctx->r4), U32(ctx->r2),\n"
    "                                  U32(ctx->r2),\n"
    "                                  (uint32_t)MEM_BU(ctx->r20, 0X4),\n"
    "                                  (uint32_t)MEM_BU(ctx->r19, -0X4),\n"
    "                                  U32(MEM_W(S32(0X8013 << 16), -0X72C0)),\n"
    "                                  (uint32_t)MEM_BU(0X0, ctx->r18));\n"
    "    }\n"
    "    // 0x80019D14: bne         $v0, $zero, L_80019D78\n"
)

D58_OLD = (
    "    // 0x80019D58: jal         0x80033E3C\n"
    "    // 0x80019D5C: nop\n"
    "\n"
    "    osSpTaskLoad_recomp(rdram, ctx);\n"
)
D58_NEW = (
    "    // 0x80019D58: jal         0x80033E3C\n"
    "    // 0x80019D5C: nop\n"
    "\n"
    "    { /* PATCH: s3300 sp busy writer */\n"
    "        rs64_s3300_sp_busy_writer(\"19D58\", 2, U32(ctx->r4), U32(ctx->r2),\n"
    "                                  (uint32_t)MEM_BU(ctx->r20, 0X0),\n"
    "                                  (uint32_t)MEM_BU(ctx->r20, 0X4),\n"
    "                                  (uint32_t)MEM_BU(ctx->r19, -0X4),\n"
    "                                  U32(MEM_W(S32(0X8013 << 16), -0X72C0)),\n"
    "                                  (uint32_t)MEM_BU(0X0, ctx->r18));\n"
    "    }\n"
    "    osSpTaskLoad_recomp(rdram, ctx);\n"
)

D78_OLD = (
    "L_80019D78:\n"
    "    // 0x80019D78: lw          $v0, 0x10($sp)\n"
    "    ctx->r2 = MEM_W(ctx->r29, 0X10);\n"
)
D78_NEW = (
    "L_80019D78:\n"
    "    // 0x80019D78: lw          $v0, 0x10($sp)\n"
    "    ctx->r2 = MEM_W(ctx->r29, 0X10);\n"
    "    { /* PATCH: s3300 sp busy writer */\n"
    "        rs64_s3300_sp_busy_writer(\"19D78\", 3, U32(ctx->r4), U32(ctx->r2),\n"
    "                                  (uint32_t)MEM_BU(ctx->r20, 0X0),\n"
    "                                  (uint32_t)MEM_BU(ctx->r20, 0X4),\n"
    "                                  (uint32_t)MEM_BU(ctx->r19, -0X4),\n"
    "                                  U32(MEM_W(S32(0X8013 << 16), -0X72C0)),\n"
    "                                  (uint32_t)MEM_BU(0X0, ctx->r18));\n"
    "    }\n"
)

DD4_OLD = (
    "    // 0x80019DD4: sb          $s1, -0x4($s3)\n"
    "    rs64_m5_writer_parity('B', 0x80019DD4u, U32(ADD32(ctx->r19, -0X4)), 0u); /* PATCH: s2190 m5 scalar */\n"
    "    rs64_probe_submit_gate_store('B', 0x80019DD4u, U32(ADD32(ctx->r19, -0X4)), U32(ctx->r17));\n"
    "    MEM_B(-0X4, ctx->r19) = ctx->r17;\n"
)
DD4_NEW = (
    "    // 0x80019DD4: sb          $s1, -0x4($s3)\n"
    "    { /* PATCH: s3300 sp busy writer */\n"
    "        rs64_s3300_sp_busy_writer(\"19DD4\", 4, U32(ctx->r4), U32(ctx->r17),\n"
    "                                  (uint32_t)MEM_BU(ctx->r20, 0X0),\n"
    "                                  (uint32_t)MEM_BU(ctx->r20, 0X4),\n"
    "                                  (uint32_t)MEM_BU(ctx->r19, -0X4),\n"
    "                                  U32(MEM_W(S32(0X8013 << 16), -0X72C0)),\n"
    "                                  (uint32_t)MEM_BU(0X0, ctx->r18));\n"
    "    }\n"
    "    rs64_m5_writer_parity('B', 0x80019DD4u, U32(ADD32(ctx->r19, -0X4)), 0u); /* PATCH: s2190 m5 scalar */\n"
    "    rs64_probe_submit_gate_store('B', 0x80019DD4u, U32(ADD32(ctx->r19, -0X4)), U32(ctx->r17));\n"
    "    MEM_B(-0X4, ctx->r19) = ctx->r17;\n"
)

FE4_OLD = (
    "    // 0x80019FE4: sb          $zero, -0x5764($at)\n"
    "    rs64_m5_writer_parity('B', 0x80019FE4u, U32(ADD32(ctx->r1, -0X5764)), 0u); /* PATCH: s2190 m5 scalar */\n"
    "    rs64_probe_submit_gate_store('B', 0x80019FE4u, U32(ADD32(ctx->r1, -0X5764)), U32(0));\n"
    "    MEM_B(-0X5764, ctx->r1) = 0;\n"
)
FE4_NEW = (
    "    // 0x80019FE4: sb          $zero, -0x5764($at)\n"
    "    { /* PATCH: s3300 sp busy writer */\n"
    "        rs64_s3300_sp_busy_writer(\"19FE4\", 5, U32(ctx->r4), 0u,\n"
    "                                  (uint32_t)MEM_BU(ctx->r20, 0X0),\n"
    "                                  (uint32_t)MEM_BU(ctx->r20, 0X4),\n"
    "                                  (uint32_t)MEM_BU(ctx->r19, -0X4),\n"
    "                                  U32(MEM_W(S32(0X8013 << 16), -0X72C0)),\n"
    "                                  (uint32_t)MEM_BU(0X0, ctx->r18));\n"
    "    }\n"
    "    rs64_m5_writer_parity('B', 0x80019FE4u, U32(ADD32(ctx->r1, -0X5764)), 0u); /* PATCH: s2190 m5 scalar */\n"
    "    rs64_probe_submit_gate_store('B', 0x80019FE4u, U32(ADD32(ctx->r1, -0X5764)), U32(0));\n"
    "    MEM_B(-0X5764, ctx->r1) = 0;\n"
)


def apply_s3300_sp_busy_writer_text(text: str):
    if MARK in text:
        return text, ["funcs_4.c: s3300 sp busy writer already present"], False
    replacements = (
        (DECL_ANCHOR, DECL_ANCHOR + HELPER + "\n"),
        (CF0T_OLD, CF0T_NEW),
        (D10_OLD, D10_NEW),
        (D58_OLD, D58_NEW),
        (D78_OLD, D78_NEW),
        (DD4_OLD, DD4_NEW),
        (FE4_OLD, FE4_NEW),
    )
    for old, new in replacements:
        n = text.count(old)
        if n != 1:
            raise RuntimeError(f"s3300 anchor count={n} for {old[:80]!r}")
        text = text.replace(old, new, 1)
    return text, ["funcs_4.c: s3300 sp busy writer probe patched x6"], True


def main():
    text, msgs, changed = apply_s3300_sp_busy_writer_text(GEN.read_text())
    for m in msgs:
        print(m)
    if changed:
        GEN.write_text(text)
        print(f"patched {GEN}")


if __name__ == "__main__":
    main()
