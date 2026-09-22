#!/usr/bin/env python3
"""Inject the s3709 caller/allocator route witness."""

from pathlib import Path


ROOT = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
CALLER = ROOT / "funcs_24.c"
CALLEE = ROOT / "funcs_23.c"
MARKER = "PATCH: s3709 M5 caller route witness"


def main() -> None:
    caller = CALLER.read_text(encoding="utf-8")
    callee = CALLEE.read_text(encoding="utf-8")
    if MARKER in caller or MARKER in callee:
        print("s3709: already applied")
        return

    caller_anchor = "    // 0x80091934: jal         0x8008F0A0\n"
    caller_insert = (
        "    { extern void rs64_m5_caller_route(const char*, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); "
        "rs64_m5_caller_route(\"caller\", 0x80091934u, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), U32(ctx->r16), U32(ctx->r17), U32(ctx->r18), U32(ctx->r19)); } "
        f"/* {MARKER} */\n"
    )
    if caller.count(caller_anchor) != 1:
        raise SystemExit(f"s3709: caller anchor count {caller.count(caller_anchor)}")
    caller = caller.replace(caller_anchor, caller_anchor + caller_insert, 1)

    callee_anchor = "RECOMP_FUNC void allocateSongChannelArray(uint8_t* rdram, recomp_context* ctx) {\n"
    callee_insert = (
        "    { extern void rs64_m5_caller_route(const char*, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); "
        "rs64_m5_caller_route(\"entry\", 0x8008F0A0u, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), U32(ctx->r16), U32(ctx->r17), U32(ctx->r18), U32(ctx->r19)); } "
        f"/* {MARKER} */\n"
    )
    if callee.count(callee_anchor) != 1:
        raise SystemExit(f"s3709: callee anchor count {callee.count(callee_anchor)}")
    callee = callee.replace(callee_anchor, callee_anchor + callee_insert, 1)

    CALLER.write_text(caller, encoding="utf-8")
    CALLEE.write_text(callee, encoding="utf-8")
    print("s3709: inserted caller and allocator route witnesses")


if __name__ == "__main__":
    main()
