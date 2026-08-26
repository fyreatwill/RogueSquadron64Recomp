#!/usr/bin/env python3
"""Add the s2463 dynamic NPC callback tuple probe to generated funcs_9.c."""

from pathlib import Path


BASE = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
TARGET = BASE / "funcs_9.c"
MARKER = "/* PATCH: s2463 m5 dynamic callback tuple */"
ANCHOR = (
    "    // 0x800400BC: sw          $s2, 0x0($s0)\n"
    "    rs64_m5_writer_parity('W', 0x800400BCu, U32(ADD32(ctx->r16, 0X0)), 0u); /* PATCH: s2190 m5 scalar */\n"
    "    rs64_probe_submit_gate_store('W', 0x800400BCu, U32(ADD32(ctx->r16, 0X0)), U32(ctx->r18));\n"
    "    MEM_W(0X0, ctx->r16) = ctx->r18;\n"
)
INSERT = (
    "    /* PATCH: s2463 m5 dynamic callback tuple */\n"
    "    { extern void rs64_m5_dynamic_callback(unsigned, unsigned, unsigned, unsigned); "
    "rs64_m5_dynamic_callback(U32(ctx->r16), U32(ctx->r18), U32(ctx->r18), U32(ctx->r31)); }\n"
)


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    if MARKER in text:
        print("apply_s2463: probe already present")
        return
    if text.count(ANCHOR) != 1:
        raise SystemExit(f"apply_s2463: expected one callback store, found {text.count(ANCHOR)}")
    text = text.replace(ANCHOR, ANCHOR + INSERT, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("apply_s2463: inserted dynamic callback tuple probe")


if __name__ == "__main__":
    main()
