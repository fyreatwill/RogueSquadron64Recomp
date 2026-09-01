"""Apply the s3529 selector input witness to the current generated output."""
from pathlib import Path


TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
MARKER = "PATCH: s3529 selector input load"


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    if MARKER in text:
        print("apply_s3529: already present")
        return
    decl = (
        "extern void rs64_m5_selector_input_load(uint32_t pc, uint32_t value, "
        "uint32_t source, uint32_t s1, uint32_t a0, uint32_t a2, uint32_t a3);\n"
    )
    anchor = '#include "funcs.h"\n'
    if text.count(anchor) != 1:
        raise SystemExit("apply_s3529: funcs.h anchor count != 1")
    text = text.replace(anchor, anchor + decl, 1)
    needle = (
        "    // 0x8009192C: lw          $a1, 0x0($s1)\n"
        "    ctx->r5 = MEM_W(ctx->r17, 0X0);\n"
    )
    insert = (
        "    rs64_m5_selector_input_load(0x8009192Cu, U32(ctx->r5), "
        "U32(ctx->r17), U32(ctx->r17), U32(ctx->r4), U32(ctx->r6), "
        "U32(ctx->r7)); /* PATCH: s3529 selector input load */\n"
    )
    if text.count(needle) != 1:
        raise SystemExit("apply_s3529: load anchor count != 1")
    TARGET.write_text(text.replace(needle, needle + insert, 1), encoding="utf-8")
    print("apply_s3529: selector input witness patched")


if __name__ == "__main__":
    main()
