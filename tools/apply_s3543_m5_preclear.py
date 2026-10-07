#!/usr/bin/env python3
"""Inject the regeneration-safe pre-clear snapshot at rs_memset entry/exit."""

from pathlib import Path


TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_2.c")
MARKER = "PATCH: s3543 M5 preclear snapshot"
SIGNATURE = "RECOMP_FUNC void rs_memset(uint8_t* rdram, recomp_context* ctx) {\n"
DECL = "extern void rs64_m5_preclear_snapshot(uint8_t*, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);\n"


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    if MARKER in text:
        required = (
            "rs64_m5_preclear_snapshot(rdram, U32(ctx->r4), U32(ctx->r5), "
            "U32(ctx->r6), U32(ctx->r31), U32(g_rs64_last_guest_pc), 0u);",
            "rs64_m5_preclear_snapshot(rdram, U32(ctx->r4), U32(ctx->r5), "
            "U32(ctx->r6), U32(ctx->r31), U32(g_rs64_last_guest_pc), 1u);",
        )
        if any(call not in text for call in required):
            raise SystemExit("s3543: partial pre-clear hook is missing an edge")
        print("s3543 pre-clear snapshot already present and complete")
        return
    if text.count(SIGNATURE) != 1:
        raise SystemExit("s3543: rs_memset signature is not unique")
    start = text.index(SIGNATURE)
    end = text.index("\n;}\n", start)
    body = text[start:end]
    if body.count("\n    return;\n") != 1:
        raise SystemExit("s3543: rs_memset return is not unique")
    hook = (
        f"    /* {MARKER} */\n"
        "    rs64_m5_preclear_snapshot(rdram, U32(ctx->r4), U32(ctx->r5), "
        "U32(ctx->r6), U32(ctx->r31), U32(g_rs64_last_guest_pc), 0u);\n"
    )
    body = body.replace(SIGNATURE, SIGNATURE + DECL + hook, 1)
    exit_hook = (
        f"    /* {MARKER} exit */\n"
        "    rs64_m5_preclear_snapshot(rdram, U32(ctx->r4), U32(ctx->r5), "
        "U32(ctx->r6), U32(ctx->r31), U32(g_rs64_last_guest_pc), 1u);\n"
    )
    body = body.replace("\n    return;\n", "\n" + exit_hook + "    return;\n", 1)
    text = text[:start] + body + text[end:]
    TARGET.write_text(text, encoding="utf-8")
    print("s3543 pre-clear snapshot injected")


if __name__ == "__main__":
    main()
