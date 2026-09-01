"""Add the regeneration-safe M5 caller witness for the selector producer."""
from pathlib import Path

TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
MARKER = "PATCH: s3500 M5 selector caller"
text = TARGET.read_text()
if MARKER in text:
    print("apply_s3500: already present")
    raise SystemExit(0)

anchor = "    musyxBuildVoiceCommandList(rdram, ctx);\n"
insert = (
    "    extern void rs64_m5_selector_caller(uint32_t caller_pc, uint32_t ra, "
    "uint32_t a0, uint32_t a1, uint32_t a2, uint32_t a3);\n"
    "    rs64_m5_selector_caller(0x80091330u, U32(ctx->r31), U32(ctx->r4), "
    "U32(ctx->r5), U32(ctx->r6), U32(ctx->r7)); /* " + MARKER + " */\n"
)
if text.count(anchor) != 1:
    raise SystemExit("apply_s3500: call anchor is not unique")
TARGET.write_text(text.replace(anchor, insert + anchor, 1))
print("apply_s3500: inserted selector caller witness")
