#!/usr/bin/env python3
from pathlib import Path

ROOT = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARKER = "PATCH: s3426 M5 init mixer args"

def main() -> None:
    path = ROOT / "funcs_24.c"
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print("s3426 init mixer witness already present")
        return

    entry = "RECOMP_FUNC void initN64RspMixer(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n"
    entry_insert = (
        "    { extern void rs64_m5_init_mixer_args(unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); "
        "rs64_m5_init_mixer_args(0u, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7)); } "
        "/* PATCH: s3426 M5 init mixer args */\n"
    )
    if text.count(entry) != 1:
        raise SystemExit("s3426: initN64RspMixer entry anchor is not unique")
    text = text.replace(entry, entry + entry_insert, 1)

    call = (
        "    // 0x80091934: jal         0x8008F0A0\n"
        "    // 0x80091938: addu        $a0, $s0, $zero\n"
        "    ctx->r4 = ADD32(ctx->r16, 0);\n"
        "    allocateSongChannelArray(rdram, ctx);\n"
    )
    call_insert = (
        "    { extern void rs64_m5_init_mixer_args(unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); "
        "rs64_m5_init_mixer_args(1u, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7)); } "
        "/* PATCH: s3426 M5 init mixer args */\n"
    )
    if text.count(call) != 1:
        raise SystemExit("s3426: init mixer allocate call anchor is not unique")
    text = text.replace(call, call.replace("    allocateSongChannelArray", call_insert + "    allocateSongChannelArray"), 1)
    path.write_text(text, encoding="utf-8")
    print("s3426 init mixer witness patched funcs_24.c")

if __name__ == "__main__":
    main()
