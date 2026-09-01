"""Add the regeneration-safe selector-store execution-context witness."""
from pathlib import Path


TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c")
MARKER = "PATCH: s3516 M5 selector-store context"
DECL = (
    "    extern void rs64_m5_selector_store_context(uint32_t pc, uint32_t v0, "
    "uint32_t s0, uint32_t s1, uint32_t s2, uint32_t a0, uint32_t a1, "
    "uint32_t a2, uint32_t a3, uint32_t ra);\n"
)


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    if MARKER in text:
        print("apply_s3516: already present")
        return
    calls = {
        "    MEM_W(-0X68A8, ctx->r1) = ctx->r2;\n":
            "    MEM_W(-0X68A8, ctx->r1) = ctx->r2;\n"
            + DECL
            + "    rs64_m5_selector_store_context(0x8008F228u, U32(ctx->r2), U32(ctx->r16), U32(ctx->r17), U32(ctx->r18), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), U32(ctx->r31)); /* " + MARKER + " */\n",
        "    MEM_W(-0X68A4, ctx->r1) = ctx->r2;\n":
            "    MEM_W(-0X68A4, ctx->r1) = ctx->r2;\n"
            + "    rs64_m5_selector_store_context(0x8008F264u, U32(ctx->r2), U32(ctx->r16), U32(ctx->r17), U32(ctx->r18), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), U32(ctx->r31)); /* " + MARKER + " */\n",
    }
    for anchor, replacement in calls.items():
        if text.count(anchor) != 1:
            raise SystemExit(f"apply_s3516: anchor count != 1: {anchor.strip()}")
        text = text.replace(anchor, replacement, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("apply_s3516: inserted selector-store context witness")


if __name__ == "__main__":
    main()
