#!/usr/bin/env python3
from pathlib import Path

GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")

def main() -> None:
    text = GEN.read_text(encoding="utf-8")
    marker = "s3428 M5 init mixer callsite"
    if marker in text:
        print("s3428 init mixer callsite witness already present")
        return

    sites = {
        "0x80091C58": "0x80091C58u",
        "0x80091D14": "0x80091D14u",
    }
    for comment_pc, arg_pc in sites.items():
        anchor = (
            f"    // {comment_pc}: jal         0x8009189C\n"
            f"    // {('0x80091C5C' if comment_pc == '0x80091C58' else '0x80091D18')}: addu        $a3, $v0, $zero\n"
            "    ctx->r7 = ADD32(ctx->r2, 0);\n"
            "    initN64RspMixer(rdram, ctx);\n"
        )
        insert = (
            "    { extern void rs64_m5_init_mixer_callsite(unsigned, unsigned, unsigned, unsigned, unsigned); "
            f"rs64_m5_init_mixer_callsite({arg_pc}, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7)); }} "
            f"/* PATCH: {marker} */\n"
        )
        if text.count(anchor) != 1:
            raise SystemExit(f"s3428: callsite anchor {comment_pc} is not unique")
        text = text.replace(anchor, anchor.replace("    initN64RspMixer", insert + "    initN64RspMixer"), 1)

    GEN.write_text(text, encoding="utf-8")
    print("s3428 init mixer callsite witness patched funcs_24.c")

if __name__ == "__main__":
    main()
