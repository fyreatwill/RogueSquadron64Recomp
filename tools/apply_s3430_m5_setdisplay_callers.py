#!/usr/bin/env python3
"""Install the regeneration-safe M5 setDisplayMode caller witnesses."""
from pathlib import Path


PATH = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c")
MARKER = "PATCH: s3430 M5 setDisplayMode caller args"


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    if MARKER in text:
        print("s3430 setDisplayMode caller witnesses already present")
        return

    anchors = (
        (
            "    // 0x8008EA78: jal         0x80091B3C\n"
            "    // 0x8008EA7C: addu        $a2, $v1, $zero\n"
            "    ctx->r6 = ADD32(ctx->r3, 0);\n",
            "set-init",
        ),
        (
            "    // 0x8008EBC0: jal         0x80091C88\n"
            "    // 0x8008EBC4: addu        $a2, $v1, $zero\n"
            "    ctx->r6 = ADD32(ctx->r3, 0);\n",
            "set-reapply",
        ),
    )
    for anchor, edge in anchors:
        if text.count(anchor) != 1:
            raise SystemExit(f"s3430: caller anchor is not unique for {edge}")
        insert = (
            "    { extern void rs64_m5_setup_state_args(const char*, unsigned, "
            "unsigned, unsigned, unsigned, unsigned); "
            f'rs64_m5_setup_state_args("{edge}", U32(ctx->r31), '
            "U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7)); } "
            f"/* {MARKER} */\n"
        )
        text = text.replace(anchor, anchor + insert, 1)
    PATH.write_text(text, encoding="utf-8")
    print("s3430 setDisplayMode caller witnesses patched funcs_23.c")


if __name__ == "__main__":
    main()
