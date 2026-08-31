#!/usr/bin/env python3
"""Install the regeneration-safe reapplyAudioConfig producer-boundary witness."""
from pathlib import Path

PATH = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
MARKER = "PATCH: s3431 M5 reapply boundary"


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    if MARKER in text:
        print("s3431 reapply boundary witness already present")
        return
    entry = (
        "RECOMP_FUNC void reapplyAudioConfig(uint8_t* rdram, recomp_context* ctx) {\n"
        "    uint64_t hi = 0, lo = 0, result = 0;\n"
    )
    entry_insert = (
        "    { extern void rs64_m5_reapply_boundary(const char*, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); "
        "rs64_m5_reapply_boundary(\"entry\", U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), 0u, 0u, 0u, 0u); } "
        f"/* {MARKER} */\n"
    )
    if text.count(entry) != 1:
        raise SystemExit("s3431: reapply entry anchor is not unique")
    text = text.replace(entry, entry + entry_insert, 1)

    start = text.index("RECOMP_FUNC void reapplyAudioConfig")
    end = text.index("\nRECOMP_FUNC void ", start + len("RECOMP_FUNC void reapplyAudioConfig"))
    body = text[start:end]

    after_freq = (
        "    MEM_W(-0X690C, ctx->r1) = ctx->r2;\n"
        "    // 0x80091CC8: sw          $v0, 0x0($s1)\n"
    )
    freq_insert = (
        "    { extern void rs64_m5_reapply_boundary(const char*, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); "
        "rs64_m5_reapply_boundary(\"after-frequency\", U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), U32(ctx->r17), U32(ctx->r18), U32(ctx->r19), U32(ctx->r2)); } "
        f"/* {MARKER} */\n"
    )
    if body.count(after_freq) != 1:
        raise SystemExit("s3431: frequency boundary anchor is not unique")
    body = body.replace(after_freq, after_freq.replace("    // 0x80091CC8", freq_insert + "    // 0x80091CC8"), 1)

    before_call = (
        "    // 0x80091D10: andi        $a2, $s3, 0xFFFF\n"
        "    ctx->r6 = ctx->r19 & 0XFFFF;\n"
        "    // 0x80091D14: jal         0x8009189C\n"
    )
    call_insert = (
        "    { extern void rs64_m5_reapply_boundary(const char*, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); "
        "rs64_m5_reapply_boundary(\"pre-mixer\", U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), U32(ctx->r17), U32(ctx->r18), U32(ctx->r19), U32(ctx->r2)); } "
        f"/* {MARKER} */\n"
    )
    if body.count(before_call) != 1:
        raise SystemExit("s3431: mixer-call boundary anchor is not unique")
    body = body.replace(before_call, before_call.replace("    // 0x80091D14", call_insert + "    // 0x80091D14"), 1)
    text = text[:start] + body + text[end:]
    PATH.write_text(text, encoding="utf-8")
    print("s3431 reapply boundary witness patched funcs_24.c")


if __name__ == "__main__":
    main()
