#!/usr/bin/env python3
"""Add the M5 caller-to-entry writer-state witness to generated functions."""

from pathlib import Path


ROOT = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARKER = "PATCH: s3423 M5 writer setup"


def main() -> None:
    caller = ROOT / "funcs_23.c"
    entry = ROOT / "funcs_2.c"
    caller_text = caller.read_text(encoding="utf-8")
    entry_text = entry.read_text(encoding="utf-8")
    if MARKER in caller_text or MARKER in entry_text:
        print("s3423 writer setup already present")
        return
    caller_anchor = (
        "    { extern void rs64_m5_static_rs_memset_callsite(unsigned, unsigned, unsigned, unsigned, unsigned); "
        "rs64_m5_static_rs_memset_callsite(0x8008F2CCu, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6)); }\n"
    )
    caller_insert = (
        "    { extern void rs64_m5_writer_setup_state(unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); "
        "rs64_m5_writer_setup_state(0x8008F2CCu, U32(ctx->r31), U32(ctx->r4), U32(ctx->r6), U32(ctx->r16), U32(ctx->r17), U32(ctx->r8), U32(ctx->r9)); } /* PATCH: s3423 M5 writer setup */\n"
    )
    if caller_text.count(caller_anchor) != 1:
        raise SystemExit("s3423: target caller anchor is not unique")
    caller_text = caller_text.replace(caller_anchor, caller_anchor + caller_insert, 1)
    entry_anchor = "    rs64_m5_writer_entry_args(ctx); /* PATCH: s3421 M5 writer entry args */\n"
    entry_insert = (
        "    { extern void rs64_m5_writer_setup_state(unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); "
        "rs64_m5_writer_setup_state(0x8008F2CCu, U32(ctx->r31), U32(ctx->r4), U32(ctx->r6), U32(ctx->r16), U32(ctx->r17), U32(ctx->r8), U32(ctx->r9)); } /* PATCH: s3423 M5 writer setup */\n"
    )
    if entry_text.count(entry_anchor) != 1:
        raise SystemExit("s3423: entry anchor is not unique")
    entry_text = entry_text.replace(entry_anchor, entry_anchor + entry_insert, 1)
    caller.write_text(caller_text, encoding="utf-8")
    entry.write_text(entry_text, encoding="utf-8")
    print("s3423 writer setup patched funcs_23.c and funcs_2.c")


if __name__ == "__main__":
    main()
