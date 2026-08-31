#!/usr/bin/env python3
"""Install the title-scoped entry control for the M5 source-writer witness."""

from pathlib import Path


GEN = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_14.c"
MARKER = "PATCH: s3460 M5 writer witness entry"

HELPER = r'''/* PATCH: s3460 M5 writer witness entry */
static void rs64_s3460_m5_writer_entry(recomp_context* ctx) {
    static int enabled = -1;
    static unsigned control = 0;
    static unsigned rows = 0;
    if (enabled < 0) {
        const char* own = getenv("ROGUESQ_LOG_M5_WRITER_PARITY");
        const char* all = getenv("ROGUESQ_LOG_ALL");
        enabled = ((own && own[0] && own[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    extern uint32_t rs64_phase_ord(void);
    unsigned width = rs64_vi_committed_width();
    unsigned origin = rs64_vi_committed_origin();
    if (width != 1024u || origin != 0x00790400u) return;
    if (!control) {
        fprintf(stderr,
                "[m5-writer-entry-control] phase=%u width=%u origin=0x%08X "
                "pc=0x80064488 a0=0x%08X a1=0x%08X a2=0x%08X "
                "s0=0x%08X s1=0x%08X ra=0x%08X\n",
                rs64_phase_ord(), width, origin, U32(ctx->r4), U32(ctx->r5),
                U32(ctx->r6), U32(ctx->r16), U32(ctx->r17), U32(ctx->r31));
        fflush(stderr);
        control = 1;
    }
    if (rows < 64u) {
        fprintf(stderr,
                "[m5-writer-entry] ordinal=%u phase=%u width=%u origin=0x%08X "
                "a0=0x%08X a1=0x%08X a2=0x%08X s0=0x%08X s1=0x%08X ra=0x%08X\n",
                rows++, rs64_phase_ord(), width, origin, U32(ctx->r4),
                U32(ctx->r5), U32(ctx->r6), U32(ctx->r16), U32(ctx->r17),
                U32(ctx->r31));
        fflush(stderr);
    }
}
'''


def main() -> None:
    text = GEN.read_text(encoding="utf-8")
    if MARKER in text:
        print("s3460 writer witness entry already present")
        return
    include = '#include "funcs.h"\n'
    entry = "RECOMP_FUNC void rebuildActiveDisplayObjectList(uint8_t* rdram, recomp_context* ctx) {\n"
    if text.count(include) != 1 or text.count(entry) != 1:
        raise SystemExit("s3460 writer witness anchors are not unique")
    text = text.replace(include, include + HELPER + "\n", 1)
    text = text.replace(
        entry,
        entry + "    rs64_s3460_m5_writer_entry(ctx); /* PATCH: s3460 M5 writer witness entry */\n",
        1,
    )
    GEN.write_text(text, encoding="utf-8")
    print("s3460 writer witness entry patched funcs_14.c")


if __name__ == "__main__":
    main()
