#!/usr/bin/env python3
"""Apply the s4938 diagnostic to the current generated funcs_24.c."""
from pathlib import Path

root = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
path = root / "funcs_24.c"
text = path.read_text()
marker = "PATCH: s4938 auxiliary store join"
if marker in text:
    print("s4938 already present")
    raise SystemExit(0)

decl = 'extern void rs64_s4938_aux_store(char, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);\n'
text = text.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + decl, 1)
sites = [
    ("    // 0x80091698: sh          $s0, -0x6678($at)\n    MEM_H(-0X6678, ctx->r1) = ctx->r16;\n", "    rs64_s4938_aux_store('H', 0x80091698u, U32(ADD32(ctx->r1, -0X6678)), U32(ctx->r16), U32(ctx->r16), U32(ctx->r17)); /* PATCH: s4938 auxiliary store join */\n"),
    ("    // 0x800916A4: sh          $v0, -0x6676($at)\n    MEM_H(-0X6676, ctx->r1) = ctx->r2;\n", "    rs64_s4938_aux_store('H', 0x800916A4u, U32(ADD32(ctx->r1, -0X6676)), U32(ctx->r2), U32(ctx->r16), U32(ctx->r17)); /* PATCH: s4938 auxiliary store join */\n"),
    ("    // 0x800917C4: sb          $v0, -0x68FE($at)\n    MEM_B(-0X68FE, ctx->r1) = ctx->r2;\n", "    rs64_s4938_aux_store('B', 0x800917C4u, U32(ADD32(ctx->r1, -0X68FE)), U32(ctx->r2), U32(ctx->r16), U32(ctx->r17)); /* PATCH: s4938 auxiliary store join */\n"),
    ("    // 0x800917F4: sw          $v0, 0x1778($at)\n    MEM_W(0X1778, ctx->r1) = ctx->r2;\n", "    rs64_s4938_aux_store('W', 0x800917F4u, U32(ADD32(ctx->r1, 0X1778)), U32(ctx->r2), U32(ctx->r16), U32(ctx->r17)); /* PATCH: s4938 auxiliary store join */\n"),
]
for anchor, insert in sites:
    if text.count(anchor) != 1:
        raise RuntimeError(f"anchor count {text.count(anchor)}: {anchor.strip()}")
    text = text.replace(anchor, anchor + insert, 1)
path.write_text(text)
print("funcs_24.c: s4938 auxiliary store join added x4")
