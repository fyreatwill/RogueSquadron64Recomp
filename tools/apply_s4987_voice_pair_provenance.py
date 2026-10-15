#!/usr/bin/env python3
"""s4987: record the voice count/base pair at each publication and observation boundary.

ORIGIN: the allocator publishes the legitimate voice-array pair; this records
that pair and does not rewrite, reject, or guard any value.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
p23 = root / "funcs_23.c"
p24 = root / "funcs_24.c"
s23 = p23.read_text()
s24 = p24.read_text()
marker = "PATCH: s4987 voice pair provenance"
if marker in s23 or marker in s24:
    print("s4987 already applied")
    raise SystemExit(0)

alloc_helper = r'''static void rs64_s4987_alloc_pair(uint8_t* rdram, uint32_t pc) {
    static int enabled = -1;
    static unsigned n = 0;
    static uint32_t last_origin = 0;
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    if (enabled < 0) { const char* e = getenv("ROGUESQ_LOG_S4987"); enabled = (e && e[0] && e[0] != '0') ? 1 : 0; }
    uint32_t origin = rs64_vi_committed_origin();
    if (origin != last_origin) { last_origin = origin; n = 0; }
    if (!enabled || rs64_vi_committed_width() < 512u || n >= 64u) return;
    n++;
    fprintf(stderr, "[s4987-pub] n=%u phase=%u origin=0x%08X pc=0x%08X base=0x%08X count=%u\n", n, rs64_vi_committed_width(), origin, pc,
        (unsigned)MEM_W(-0x6908, S32(0x8015 << 16)), (unsigned)MEM_HU(-0x6900, S32(0x8015 << 16)));
    fflush(stderr);
}
/* PATCH: s4987 voice pair provenance */
'''
obs_helper = r'''static void rs64_s4987_obs_pair(uint8_t* rdram, uint32_t pc, uint32_t count, uint32_t base) {
    static int enabled = -1;
    static unsigned n = 0;
    static uint32_t last_origin = 0;
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    if (enabled < 0) { const char* e = getenv("ROGUESQ_LOG_S4987"); enabled = (e && e[0] && e[0] != '0') ? 1 : 0; }
    uint32_t origin = rs64_vi_committed_origin();
    if (origin != last_origin) { last_origin = origin; n = 0; }
    if (!enabled || rs64_vi_committed_width() < 512u || n >= 128u) return;
    n++;
    fprintf(stderr, "[s4987-obs] n=%u phase=%u origin=0x%08X pc=0x%08X load_count=%u load_base=0x%08X guest_count=%u guest_base=0x%08X\n", n,
        rs64_vi_committed_width(), origin, pc, count, base,
        (unsigned)MEM_HU(-0x6900, S32(0x8015 << 16)), (unsigned)MEM_W(-0x6908, S32(0x8015 << 16)));
    fflush(stderr);
}
/* PATCH: s4987 voice pair provenance */
'''
anchor23 = "RECOMP_FUNC void allocateSongChannelArray(uint8_t* rdram, recomp_context* ctx) {\n"
anchor24 = "RECOMP_FUNC void musyxMixActiveVoices(uint8_t* rdram, recomp_context* ctx) {\n"
if s23.count(anchor23) != 1 or s24.count(anchor24) != 1:
    raise SystemExit("function anchor count mismatch")
s23 = s23.replace(anchor23, alloc_helper + anchor23, 1)
s24 = s24.replace(anchor24, obs_helper + anchor24, 1)

needle23 = "    rs64_s4985_voice_unlock(); /* PATCH: s4986 narrow voice lock publication exit */\n"
if s23.count(needle23) != 1:
    raise SystemExit(f"publication anchor count={s23.count(needle23)}")
s23 = s23.replace(needle23, needle23 + "    rs64_s4987_alloc_pair(rdram, 0x8008F0CCu);\n", 1)

needle24_count = "    { uint32_t s4575_a = U32(ADD32(ctx->r4, -0X6900)); ctx->r4 = rs64_s4984_load_voice_count(rdram); rs64_s4307_synth_read(rdram, 0x80090E1Cu, s4575_a, U32(ctx->r4)); } /* PATCH: s4984 atomic count load */\n"
if s24.count(needle24_count) != 1:
    raise SystemExit(f"count observation anchor count={s24.count(needle24_count)}")
s24 = s24.replace(needle24_count, needle24_count + "    uint32_t rs64_s4987_observed_count = U32(ctx->r4);\n", 1)
needle24 = "    rs64_s4985_voice_unlock(); /* PATCH: s4986 narrow voice lock observation exit */\n"
if s24.count(needle24) != 1:
    raise SystemExit(f"observation anchor count={s24.count(needle24)}")
replacement24 = needle24 + "    rs64_s4987_obs_pair(rdram, 0x80090E78u, rs64_s4987_observed_count, rs64_s4984_load_voice_base(rdram));\n"
s24 = s24.replace(needle24, replacement24, 1)

p23.write_text(s23)
p24.write_text(s24)
print("s4987 voice pair provenance applied")
