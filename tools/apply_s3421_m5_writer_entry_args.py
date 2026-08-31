#!/usr/bin/env python3
"""Apply the M5 writer-entry witness to the companion generated funcs_2.c."""

from pathlib import Path


TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_2.c")
MARKER = "PATCH: s3421 M5 writer entry args"
HELPER = r'''/* PATCH: s3421 M5 writer entry args */
static void rs64_m5_writer_entry_args(recomp_context* ctx) {
    static int enabled = -1;
    static uint32_t bucket = 0xFFFFFFFFu;
    static unsigned control_rows = 0;
    static unsigned target_rows = 0;
    if (enabled < 0) {
        const char* all = getenv("ROGUESQ_LOG_ALL");
        const char* own = getenv("ROGUESQ_LOG_M5_WRITER_ENTRY");
        enabled = ((all && all[0] && all[0] != '0') ||
                   (own && own[0] && own[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    extern uint32_t rs64_phase_ord(void);
    uint32_t width = rs64_vi_committed_width();
    uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;
    uint32_t next_bucket = (width << 24) ^ origin;
    if (next_bucket != bucket) {
        bucket = next_bucket;
        control_rows = 0;
        target_rows = 0;
    }
    uint32_t a0 = U32(ctx->r4);
    uint32_t a1 = U32(ctx->r5);
    uint32_t a2 = U32(ctx->r6);
    uint32_t v0 = a0;
    uint32_t end = a0 + a2;
    unsigned target = a2 != 0u && a0 < 0x80179A48u && end > 0x801797B0u;
    unsigned *budget = target ? &target_rows : &control_rows;
    unsigned limit = target ? 64u : 8u;
    if (*budget >= limit) return;
    if (*budget == 0u && !target) {
        fprintf(stderr, "[m5-writer-entry-control] phase=%u width=%u origin=0x%06X a0=0x%08X a1=0x%08X a2=0x%X v0=0x%08X ra=0x%08X\n",
                rs64_phase_ord(), width, origin, a0, a1, a2, v0, U32(ctx->r31));
        fflush(stderr);
    }
    fprintf(stderr, "[m5-writer-entry] n=%u target=%u phase=%u width=%u origin=0x%06X a0=0x%08X a1=0x%08X a2=0x%X v0=0x%08X ra=0x%08X callsite=0x%08X\n",
            *budget, target, rs64_phase_ord(), width, origin, a0, a1, a2, v0,
            U32(ctx->r31), U32(ctx->r31) >= 8u ? U32(ctx->r31) - 8u : 0u);
    fflush(stderr);
    ++*budget;
}
'''


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    if MARKER in text:
        print("s3421 writer entry args already present")
        return
    include = '#include "funcs.h"\n'
    entry = "RECOMP_FUNC void rs_memset(uint8_t* rdram, recomp_context* ctx) {\n"
    if text.count(include) != 1 or text.count(entry) != 1:
        raise SystemExit("s3421 funcs_2.c anchors are not unique")
    text = text.replace(include, include + HELPER + "\n", 1)
    text = text.replace(
        entry,
        entry + "    rs64_m5_writer_entry_args(ctx); /* PATCH: s3421 M5 writer entry args */\n",
        1,
    )
    TARGET.write_text(text, encoding="utf-8")
    print("s3421 writer entry args patched funcs_2.c")


if __name__ == "__main__":
    main()
