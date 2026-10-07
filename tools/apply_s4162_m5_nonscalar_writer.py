#!/usr/bin/env python3
"""Inject the regeneration-safe M5 non-scalar destination census."""

from pathlib import Path


BASE = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARKER = "PATCH: s4162 M5 non-scalar destination census"


def inject(path: Path, signature: str, call: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    if text.count(signature) != 1:
        raise SystemExit(f"{path}: expected one function signature")
    text = text.replace(signature, signature + call, 1)
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    memset = BASE / "funcs_2.c"
    memcpy = BASE / "funcs_4.c"
    changed = 0
    changed += inject(
        memset,
        "RECOMP_FUNC void rs_memset(uint8_t* rdram, recomp_context* ctx) {\n",
        "    /* PATCH: s4162 M5 non-scalar destination census */\n"
        "    { extern void rs64_m5_preclear_nonscalar(uint8_t*, char, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);\n"
        "      rs64_m5_preclear_nonscalar(rdram, 'S', 0x800078E0u, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r31)); }\n",
    )
    changed += inject(
        memcpy,
        "RECOMP_FUNC void zmemcpy(uint8_t* rdram, recomp_context* ctx) {\n",
        "    /* PATCH: s4162 M5 non-scalar destination census */\n"
        "    { extern void rs64_m5_preclear_nonscalar(uint8_t*, char, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);\n"
        "      rs64_m5_preclear_nonscalar(rdram, 'M', 0x80018EF4u, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r31)); }\n",
    )
    print(f"s4162 non-scalar census patched {changed} generated files")


if __name__ == "__main__":
    main()
