#!/usr/bin/env python3
"""Install the regeneration-safe sole zcfree-to-rs_free edge witness."""
from pathlib import Path


BASE = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARKER = "PATCH: s3476 zcfree edge"
DECL = "extern void rs64_m5_zcfree_edge(recomp_context* ctx);\n"


def main() -> None:
    path = BASE / "funcs_7.c"
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print("s3476 zcfree edge already installed")
        return
    anchor = "#include \"funcs.h\"\n"
    if text.count(anchor) != 1:
        raise SystemExit("funcs.h anchor count mismatch")
    text = text.replace(anchor, anchor + DECL, 1)
    old = "    ctx->r4 = ADD32(ctx->r5, 0);\n    rs_zcfree(rdram, ctx);\n"
    new = ("    ctx->r4 = ADD32(ctx->r5, 0);\n"
           f"    rs64_m5_zcfree_edge(ctx); /* {MARKER} */\n"
           "    rs_zcfree(rdram, ctx);\n")
    if text.count(old) != 1:
        raise SystemExit(f"expected one zcfree edge, found {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("s3476 zcfree edge patched funcs_7.c")


if __name__ == "__main__":
    main()
