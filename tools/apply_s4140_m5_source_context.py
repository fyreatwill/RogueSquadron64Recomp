#!/usr/bin/env python3
"""Add the regeneration-replayable source-context hook for s4140."""

from pathlib import Path


TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_2.c")
MARKER = "PATCH: s4140 M5 source context"


def main() -> int:
    text = TARGET.read_text()
    if MARKER in text:
        print("s4140: already applied")
        return 0
    declaration = (
        "extern void rs64_m5_source_context(uint8_t*, uint32_t pc, uint32_t ra,\n"
        "                                  uint32_t a0, uint32_t a1, uint32_t a2,\n"
        "                                  uint32_t a3, uint32_t source_ptr,\n"
        "                                  uint32_t destination, uint32_t value);\n"
    )
    anchor = '#include "funcs.h"\n'
    if text.count(anchor) != 1:
        raise RuntimeError(f"include anchor count={text.count(anchor)}")
    text = text.replace(anchor, anchor + declaration, 1)
    old = (
        "    rs64_m5_writer_parity('B', 0x800078ECu, U32(ADD32(ctx->r2, 0X0)), 0u); /* PATCH: s2190 m5 scalar */\n"
        "    rs64_probe_submit_gate_store('B', 0x800078ECu, U32(ADD32(ctx->r2, 0X0)), U32(ctx->r5));\n"
    )
    new = old + (
        "    rs64_m5_source_context(rdram, 0x800078ECu, U32(ctx->r31),\n"
        "                         U32(ctx->r4), U32(ctx->r5), U32(ctx->r6),\n"
        "                         U32(ctx->r7), U32(ctx->r2),\n"
        "                         U32(ctx->r4), U32(ctx->r5)); /* " + MARKER + " */\n"
    )
    if text.count(old) != 1:
        raise RuntimeError(f"writer anchor count={text.count(old)}")
    TARGET.write_text(text.replace(old, new, 1))
    print("s4140: patched funcs_2.c")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
