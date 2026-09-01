#!/usr/bin/env python3
"""Reapply the selector AI callsite probe after RecompiledFuncs regeneration."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT.parent / "N64Recomp" / "RecompiledFuncs" / "funcs_24.c"
DECL = "extern void rs64_m5_selector_ai_callsite(uint32_t callsite, uint32_t a0, uint32_t a1, uint32_t a2, uint32_t s0, uint32_t s1, uint32_t v0);\n"


def patch(text: str) -> str:
    anchor = 'extern void rs64_m5_mix_entry(uint8_t* rdram, recomp_context* ctx, uint32_t pc);\n'
    if DECL.strip() not in text:
        if anchor not in text:
            raise SystemExit('selector probe declaration anchor not found')
        text = text.replace(anchor, anchor + DECL, 1)
    for callsite in ("0x80091BACu", "0x80091CB8u"):
        marker = f"    // {callsite[:-1]}: jal         0x80029D20\n"
        probe = (
            f"    rs64_m5_selector_ai_callsite({callsite}, U32(ctx->r4), U32(ctx->r5),\n"
            "                                 U32(ctx->r6), U32(ctx->r16), U32(ctx->r17), U32(ctx->r2));\n"
        )
        if probe not in text:
            if marker not in text:
                raise SystemExit(f'{callsite} anchor not found')
            text = text.replace(marker, marker + probe, 1)
    return text


if __name__ == '__main__':
    if not TARGET.exists():
        raise SystemExit(f'missing generated file: {TARGET}')
    before = TARGET.read_text()
    after = patch(before)
    if after == before:
        print('selector callsite probe already present')
    else:
        TARGET.write_text(after)
        print(f'patched {TARGET}')
