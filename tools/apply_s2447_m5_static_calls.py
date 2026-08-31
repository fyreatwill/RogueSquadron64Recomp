#!/usr/bin/env python3
"""Add the s2447 rs_memset entry table to generated funcs_2.c."""

from pathlib import Path


BASE = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
TARGET = BASE / "funcs_2.c"
MARKER = "/* PATCH: s2447 m5 static rs_memset entry table */"

HELPER = r'''/* PATCH: s2447 m5 static rs_memset entry table */
static void rs64_m5_static_rs_memset_entry(recomp_context* ctx) {
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    extern unsigned char rs64_audio_current_route_snapshot(
        uint32_t*, uint32_t*, uint32_t*, uint32_t*, uint32_t*, int*, const char**);
    extern volatile uint32_t g_rs64_last_guest_pc;
    extern uint32_t rs64_m5_static_rs_memset_last_callsite(void);
    extern uint32_t rs64_m5_static_rs_memset_last_ra(void);
    static int enabled = -1;
    static unsigned rows = 0;
    static unsigned target_rows = 0;
    static unsigned control_rows = 0;
    static uint32_t bucket = 0xFFFFFFFFu;
    if (enabled < 0) {
        const char* e = getenv("ROGUESQ_LOG_M5_STATIC_CALLS");
        const char* all = getenv("ROGUESQ_LOG_ALL");
        enabled = ((e && e[0] && e[0] != '0') ||
                   (all && all[0] && all[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    uint32_t width = rs64_vi_committed_width();
    uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x00790400u) ||
          (width == 512u && origin == 0x006AB400u))) return;
    uint32_t next_bucket = (width << 24) ^ origin;
    if (next_bucket != bucket) {
        bucket = next_bucket;
        rows = 0;
        target_rows = 0;
        control_rows = 0;
    }
    uint32_t dst = U32(ctx->r4);
    uint32_t len = U32(ctx->r6);
    uint32_t end = dst + len;
    unsigned target = len != 0u && dst < 0x80179A48u && end > 0x801797B0u;
    if (target ? target_rows >= 512u : control_rows >= 16u) return;
    uint32_t phase = rs64_phase_ord();
    uint32_t ordinal = 0xFFFFFFFFu, row = 0xFFFFFFFFu;
    int exit_reason = 0;
    const char* arm = "n/a";
    unsigned active = rs64_audio_current_route_snapshot(
        &phase, &width, &origin, &ordinal, &row, &exit_reason, &arm) ? 1u : 0u;
    uint32_t ra = U32(ctx->r31);
    uint32_t callsite = ra >= 8u ? ra - 8u : 0u;
    fprintf(stderr,
        "[m5-static-rsmemset] n=%u target=%u entry=0x800078E0 ra=0x%08X "
        "caller_callsite=0x%08X caller_ra=0x%08X "
        "callsite=0x%08X breadcrumb=0x%08X phase=%u width=%u "
        "origin=0x%06X arm=%s ordinal=%u row=%u active=%u "
        "dst=0x%08X val=0x%08X len=0x%X exit=%d\n",
        rows, target, ra, callsite, rs64_m5_static_rs_memset_last_callsite(),
        rs64_m5_static_rs_memset_last_ra(), (unsigned)g_rs64_last_guest_pc, phase, width,
        origin, arm ? arm : "n/a", ordinal, row, active,
        dst, U32(ctx->r5), len, exit_reason);
    fflush(stderr);
    ++rows;
    if (target) ++target_rows; else ++control_rows;
}
'''


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    if MARKER in text:
        start = text.index(MARKER)
        end = text.index("\n\nstatic int s_process_scene_node_depth;", start)
        text = text[:start] + HELPER + "\n" + text[end:]
        TARGET.write_text(text, encoding="utf-8")
        print("apply_s2447: refreshed static rs_memset entry table")
        return
    marker = "RECOMP_FUNC void rs_memset(uint8_t* rdram, recomp_context* ctx) {\n"
    if text.count(marker) != 1:
        raise SystemExit(f"apply_s2447: expected one rs_memset body, found {text.count(marker)}")
    text = text.replace(marker, marker + "    rs64_m5_static_rs_memset_entry(ctx);\n", 1)
    include = '#include "funcs.h"\n'
    if text.count(include) != 1:
        raise SystemExit("apply_s2447: funcs.h include anchor mismatch")
    text = text.replace(include, include + HELPER + "\n", 1)
    TARGET.write_text(text, encoding="utf-8")
    print("apply_s2447: inserted static rs_memset entry table")


if __name__ == "__main__":
    main()
