"""Add the regeneration-safe selector-producer entry-context witness."""
from pathlib import Path


TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
MARKER = "PATCH: s3517 M5 selector producer context"
ANCHOR = "    { extern void rs64_m5_init_mixer_args(unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); rs64_m5_init_mixer_args(0u, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7)); } /* PATCH: s3426 M5 init mixer args */\n"
INSERT = ANCHOR + (
    "    { extern void rs64_m5_selector_producer_context(unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); "
    "rs64_m5_selector_producer_context(0x8009189Cu, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), U32(ctx->r16), U32(ctx->r17), U32(ctx->r18)); } /* " + MARKER + " */\n"
)


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    if MARKER in text:
        print("apply_s3517: already present")
        return
    if text.count(ANCHOR) != 1:
        raise SystemExit("apply_s3517: mixer entry anchor count != 1")
    TARGET.write_text(text.replace(ANCHOR, INSERT, 1), encoding="utf-8")
    print("apply_s3517: inserted selector producer context witness")


if __name__ == "__main__":
    main()
