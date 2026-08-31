#!/usr/bin/env python3
"""Install the regeneration-safe M5 setup-state entry witness."""
from pathlib import Path


ROOT = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
PATH = ROOT / "funcs_24.c"
MARKER = "PATCH: s3429 M5 setup state args"


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    if MARKER in text:
        print("s3429 setup-state witness already present")
        return

    anchors = (
        (
            "RECOMP_FUNC void initAudioSubsystem(uint8_t* rdram, recomp_context* ctx) {\n"
            "    uint64_t hi = 0, lo = 0, result = 0;\n",
            "init",
        ),
        (
            "RECOMP_FUNC void reapplyAudioConfig(uint8_t* rdram, recomp_context* ctx) {\n"
            "    uint64_t hi = 0, lo = 0, result = 0;\n",
            "reapply",
        ),
    )
    for anchor, edge in anchors:
        if text.count(anchor) != 1:
            raise SystemExit(f"s3429: entry anchor is not unique for {edge}")
        insert = (
            f"    {{ extern void rs64_m5_setup_state_args(const char*, unsigned, unsigned, unsigned, unsigned, unsigned); "
            f"rs64_m5_setup_state_args(\"{edge}\", U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7)); }} "
            f"/* {MARKER} */\n"
        )
        text = text.replace(anchor, anchor + insert, 1)
    PATH.write_text(text, encoding="utf-8")
    print("s3429 setup-state witness patched funcs_24.c")


if __name__ == "__main__":
    main()
