#!/usr/bin/env python3
"""Inject the scheduler event/task identity probe at its generated boundary."""

from pathlib import Path
import re


GEN = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
MARKER = "/* PATCH: s2484 m5 scheduler identity */"
INSERT = (
    f"    {MARKER}\n"
    "    { extern void rs64_m5_scheduler_handoff(uint8_t*, unsigned, unsigned, unsigned); "
    "rs64_m5_scheduler_handoff(rdram, U32(ctx->r4), U32(ctx->r2), "
    "U32(ctx->r2)); }\n"
)


def main() -> None:
    path = GEN / "funcs_4.c"
    text = path.read_text(encoding="utf-8")
    needle = "    // 0x80019D28: lw          $v0, 0x4($a0)\n    ctx->r2 = MEM_W(ctx->r4, 0X4);\n"
    if text.count(needle) != 1:
        raise SystemExit(f"expected one scheduler load boundary, found {text.count(needle)}")
    text = re.sub(
        r"(?m)^\s*/\* PATCH: s2484 m5 scheduler identity \*/\n"
        r"\s*\{ extern void rs64_m5_scheduler_handoff\([^\n]+\n",
        "",
        text,
    )
    replacement = needle + INSERT
    path.write_text(text.replace(needle, replacement, 1), encoding="utf-8")
    print("apply_s2484: inserted scheduler identity probe")


if __name__ == "__main__":
    main()
