#!/usr/bin/env python3
"""Add the route-caller witness at the only two selector setup callers."""
from pathlib import Path

TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c")
MARKER = "PATCH: s3522 M5 selector route caller"
text = TARGET.read_text()
if MARKER in text:
    print("apply_s3522: already present")
    raise SystemExit(0)

text = text.replace(
    "extern void rs64_m5_state_pointer_callsite(recomp_context* ctx, uint32_t call_pc);\n",
    "extern void rs64_m5_state_pointer_callsite(recomp_context* ctx, uint32_t call_pc);\n"
    "extern void rs64_m5_selector_route_caller(const char* name, uint32_t pc, uint32_t ra, uint32_t a0, uint32_t a1, uint32_t a2, uint32_t a3);\n",
    1,
)
anchors = [
    ("RECOMP_FUNC void setDisplayMode(uint8_t* rdram, recomp_context* ctx) {",
     '    rs64_m5_selector_route_caller("setDisplayMode", 0x8008EA14u, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7)); /* PATCH: s3522 M5 selector route caller */\n'),
    ("RECOMP_FUNC void reapplyDisplayMode(uint8_t* rdram, recomp_context* ctx) {",
     '    rs64_m5_selector_route_caller("reapplyDisplayMode", 0x8008EB5Cu, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7)); /* PATCH: s3522 M5 selector route caller */\n'),
]
for anchor, insert in anchors:
    if text.count(anchor) != 1:
        raise SystemExit(f"apply_s3522: anchor count for {anchor}: {text.count(anchor)}")
    text = text.replace(anchor, anchor + insert, 1)
TARGET.write_text(text)
print("apply_s3522: inserted 2 route caller witnesses")
