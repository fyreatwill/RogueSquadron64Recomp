"""Add the regeneration-safe M5 selector pre-call witness."""
from pathlib import Path

TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
MARKER = "PATCH: s3501 M5 selector pre-call"
text = TARGET.read_text()
if MARKER in text:
    print("apply_s3501: already present")
    raise SystemExit(0)

anchor_a0 = "    // 0x8009131C: lw          $a0, -0x68F8($at)\n    ctx->r4 = MEM_W(ctx->r1, -0X68F8);\n"
insert_a0 = (
    "    extern void rs64_m5_selector_precall(uint32_t pc, uint32_t stage, "
    "uint32_t index, uint32_t address, uint32_t value, uint32_t a0, "
    "uint32_t a1, uint32_t a2, uint32_t s0, uint32_t s1);\n"
    "    rs64_m5_selector_precall(0x8009131Cu, 0u, U32(ctx->r2), U32(ctx->r1), "
    "U32(ctx->r4), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r16), "
    "U32(ctx->r17)); /* " + MARKER + " a0 */\n"
)
if text.count(anchor_a0) != 1:
    raise SystemExit("apply_s3501: a0 load anchor is not unique")
text = text.replace(anchor_a0, anchor_a0 + insert_a0, 1)

anchor_a1 = "    // 0x8009132C: lhu         $a1, -0x68F0($at)\n    ctx->r5 = MEM_HU(ctx->r1, -0X68F0);\n"
insert_a1 = (
    "    rs64_m5_selector_precall(0x8009132Cu, 1u, U32(ctx->r2), U32(ctx->r1), "
    "U32(ctx->r5), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r16), "
    "U32(ctx->r17)); /* " + MARKER + " a1 */\n"
)
if text.count(anchor_a1) != 1:
    raise SystemExit("apply_s3501: a1 load anchor is not unique")
text = text.replace(anchor_a1, anchor_a1 + insert_a1, 1)
TARGET.write_text(text)
print("apply_s3501: inserted selector pre-call witness")
