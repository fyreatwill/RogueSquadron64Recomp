#!/usr/bin/env python3
"""Inject the s3708 branch/route witness at the clear caller's control edges."""

from pathlib import Path


GEN = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
TARGET = GEN / "funcs_23.c"
MARKER = "/* PATCH: s3708 M5 clear branch witness */"


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    if MARKER in text:
        print("s3708: already applied")
        return
    specs = [
        ("    // 0x8008F108: beq         $v1, $zero, L_8008F170\n",
         "    { extern void rs64_m5_clear_branch(unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); "
         "rs64_m5_clear_branch(0x8008F108u, U32(ctx->r2) == 0u, U32(ctx->r2), U32(ctx->r3), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r16), U32(ctx->r17), U32(ctx->r31)); } " + MARKER + "\n"),
        ("    // 0x8008F168: bne         $v0, $zero, L_8008F118\n",
         "    { extern void rs64_m5_clear_branch(unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); "
         "rs64_m5_clear_branch(0x8008F168u, U32(ctx->r2) != 0u, U32(ctx->r2), U32(ctx->r3), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r16), U32(ctx->r17), U32(ctx->r31)); } " + MARKER + "\n"),
        ("    // 0x8008F1C4: bc1tl       L_8008F1DC\n",
         "    { extern void rs64_m5_clear_branch(unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); "
         "rs64_m5_clear_branch(0x8008F1C4u, c1cs != 0, U32(ctx->r2), U32(ctx->r3), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r16), U32(ctx->r17), U32(ctx->r31)); } " + MARKER + "\n"),
    ]
    for anchor, insertion in specs:
        if text.count(anchor) != 1:
            raise SystemExit(f"s3708: expected one anchor, found {text.count(anchor)}: {anchor.strip()}")
        text = text.replace(anchor, anchor + insertion, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("s3708: injected 3 clear-caller branch witnesses in funcs_23.c")


if __name__ == "__main__":
    main()
