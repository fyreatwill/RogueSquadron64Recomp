#!/usr/bin/env python3
"""Inject s3302 0x8011A89F clear/restore ordering probes into funcs_4.c.

Sites: L_80019F50 entry, post-store 0x80019F6C, and post-store
0x80019E60 / 0x80019E70. Keep the existing viewer, submit, scheduler,
dispatch, type-2, and 89C probes. Diagnostic only.

This patches an already-sentinel'd RecompiledFuncs/funcs_4.c without
re-running the full fixup. The same transform is called from
../N64Recomp/fixup_game_funcs.py for the next clear+regen+fixup.
"""
from pathlib import Path


GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c")
MARK = "PATCH: s3302 89f clear"

HELPER = r'''
static void rs64_s3302_89f_clear(uint8_t* rdram, const char* site, int idx, uint32_t s2b0,
                                 uint32_t s0, uint32_t s1) {
    static unsigned long n[4];
    static unsigned long seq;
    unsigned long c = ++n[idx];
    unsigned long q = ++seq;
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    {
        uint32_t width = rs64_vi_committed_width();
        if (width < 640u && c > 10ul && (c % 50ul) != 0ul) return;
        fprintf(stderr,
                "[s3302-89f] site=%s n=%lu seq=%lu s2b0=0x%02X sp89c=0x%02X sp89f=0x%02X yieldw=0x%08X s0=0x%08X s1=0x%08X phase=%u width=%u origin=0x%06X\n",
                site, c, q, s2b0 & 0xFFu,
                (uint32_t)MEM_BU(S32(0X8012 << 16), -0X5764) & 0xFFu,
                (uint32_t)MEM_BU(S32(0X8012 << 16), -0X5761) & 0xFFu,
                U32(MEM_W(S32(0X8013 << 16), -0X72C0)), s0, s1,
                rs64_phase_ord(), width,
                rs64_vi_committed_origin() & 0x00FFFFFFu);
    }
    fflush(stderr);
}
'''

DECL_ANCHOR = '#include "funcs.h"\n'

E60_OLD = (
    "    // 0x80019E60: sb          $zero, -0x5761($at)\n"
    "    rs64_m5_writer_parity('B', 0x80019E60u, U32(ADD32(ctx->r1, -0X5761)), 0u); /* PATCH: s2190 m5 scalar */\n"
    "    rs64_probe_submit_gate_store('B', 0x80019E60u, U32(ADD32(ctx->r1, -0X5761)), U32(0));\n"
    "    MEM_B(-0X5761, ctx->r1) = 0;\n"
)
E60_NEW = E60_OLD + (
    "    { /* PATCH: s3302 89f clear */\n"
    "        rs64_s3302_89f_clear(rdram, \"19E60-post\", 0, (uint32_t)MEM_BU(0X0, ctx->r18),\n"
    "                                U32(ctx->r16), U32(ctx->r17));\n"
    "    }\n"
)

E70_OLD = (
    "    // 0x80019E70: sb          $s1, -0x5761($at)\n"
    "    rs64_m5_writer_parity('B', 0x80019E70u, U32(ADD32(ctx->r1, -0X5761)), 0u); /* PATCH: s2190 m5 scalar */\n"
    "    rs64_probe_submit_gate_store('B', 0x80019E70u, U32(ADD32(ctx->r1, -0X5761)), U32(ctx->r17));\n"
    "    MEM_B(-0X5761, ctx->r1) = ctx->r17;\n"
)
E70_NEW = E70_OLD + (
    "    { /* PATCH: s3302 89f clear */\n"
    "        rs64_s3302_89f_clear(rdram, \"19E70-post\", 1, (uint32_t)MEM_BU(0X0, ctx->r18),\n"
    "                                U32(ctx->r16), U32(ctx->r17));\n"
    "    }\n"
)

F50_OLD = (
    "L_80019F50:\n"
    "    // 0x80019F50: lui         $a0, 0x8012\n"
)
F50_NEW = (
    "L_80019F50:\n"
    "    { /* PATCH: s3302 89f clear */\n"
    "        rs64_s3302_89f_clear(rdram, \"19F50\", 2, (uint32_t)MEM_BU(0X0, ctx->r18),\n"
    "                                U32(ctx->r16), U32(ctx->r17));\n"
    "    }\n"
    "    // 0x80019F50: lui         $a0, 0x8012\n"
)

F6C_OLD = (
    "    // 0x80019F6C: sb          $zero, 0x0($s2)\n"
    "    rs64_m5_writer_parity('B', 0x80019F6Cu, U32(ADD32(ctx->r18, 0X0)), 0u); /* PATCH: s2190 m5 scalar */\n"
    "    rs64_probe_submit_gate_store('B', 0x80019F6Cu, U32(ADD32(ctx->r18, 0X0)), U32(0));\n"
    "    MEM_B(0X0, ctx->r18) = 0;\n"
)
F6C_NEW = F6C_OLD + (
    "    { /* PATCH: s3302 89f clear */\n"
    "        rs64_s3302_89f_clear(rdram, \"19F6C-post\", 3, (uint32_t)MEM_BU(0X0, ctx->r18),\n"
    "                                U32(ctx->r16), U32(ctx->r17));\n"
    "    }\n"
)


def apply_s3302_89f_clear_text(text: str):
    if MARK in text:
        return text, ["funcs_4.c: s3302 89f clear already present"], False
    replacements = (
        (DECL_ANCHOR, DECL_ANCHOR + HELPER + "\n"),
        (E60_OLD, E60_NEW),
        (E70_OLD, E70_NEW),
        (F50_OLD, F50_NEW),
        (F6C_OLD, F6C_NEW),
    )
    for old, new in replacements:
        n = text.count(old)
        if n != 1:
            raise RuntimeError(f"s3302 anchor count={n} for {old[:80]!r}")
        text = text.replace(old, new, 1)
    return text, ["funcs_4.c: s3302 89f clear probe patched x4"], True


def main():
    text, msgs, changed = apply_s3302_89f_clear_text(GEN.read_text())
    for msg in msgs:
        print(msg)
    if changed:
        GEN.write_text(text)
        print(f"patched {GEN}")


if __name__ == "__main__":
    main()
