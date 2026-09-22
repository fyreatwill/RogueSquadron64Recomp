#!/usr/bin/env python3
"""Carry RDRAM into the s3707 M5 clear-input witness at both call edges."""

from pathlib import Path


ROOT = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARKER = "PATCH: s3707 M5 clear input witness"
OLD_CALLER = "rs64_m5_writer_setup_state(0x8008F2CCu, U32(ctx->r31), U32(ctx->r4), U32(ctx->r6), U32(ctx->r16), U32(ctx->r17), U32(ctx->r8), U32(ctx->r9));"
NEW_CALLER = "rs64_m5_writer_setup_state(rdram, 0x8008F2CCu, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r16), U32(ctx->r17), U32(ctx->r8), U32(ctx->r9)); /* " + MARKER + " */"
OLD_ENTRY = "rs64_m5_writer_setup_state(0x8008F2CCu, U32(ctx->r31), U32(ctx->r4), U32(ctx->r6), U32(ctx->r16), U32(ctx->r17), U32(ctx->r8), U32(ctx->r9));"
NEW_ENTRY = "rs64_m5_writer_setup_state(rdram, 0x800078E0u, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r16), U32(ctx->r17), U32(ctx->r8), U32(ctx->r9)); /* " + MARKER + " */"
DECL_OLD = "extern void rs64_m5_writer_setup_state(unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned);"
DECL_NEW = "extern void rs64_m5_writer_setup_state(uint8_t*, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned);"


def main() -> None:
    changed = 0
    for name in ("funcs_2.c", "funcs_23.c"):
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        if MARKER in text:
            if DECL_OLD in text:
                text = text.replace(DECL_OLD, DECL_NEW, 1)
                text = text.replace(NEW_CALLER, NEW_CALLER.replace("0x8008F2CCu", "0x8008F2CCu").replace("U32(ctx->r4), U32(ctx->r6)", "U32(ctx->r4), U32(ctx->r5), U32(ctx->r6)"), 1)
                path.write_text(text, encoding="utf-8")
                changed += 1
            continue
        old = OLD_ENTRY if name == "funcs_2.c" else OLD_CALLER
        new = NEW_ENTRY if name == "funcs_2.c" else NEW_CALLER
        if text.count(old) != 1:
            raise SystemExit(f"s3707: expected one setup call in {name}")
        text = text.replace(DECL_OLD, DECL_NEW, 1)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        changed += 1
    if changed != 2:
        raise SystemExit(f"s3707: patched {changed} generated files, expected 2")
    print("s3707 M5 clear-input witness patched funcs_2.c and funcs_23.c")


if __name__ == "__main__":
    main()
