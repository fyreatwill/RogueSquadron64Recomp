#!/usr/bin/env python3
"""Install the regeneration-safe M5 writer-loop state witness."""

from pathlib import Path


GEN = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_2.c"
MARKER = "PATCH: s3421 M5 writer-loop state"

HELPER = r'''/* PATCH: s3421 M5 writer-loop state */
static uint32_t rs64_m5_writer_state_word(uint8_t* rdram, uint32_t guest,
                                           uint32_t offset) {
    if (guest < 0x80000000u || guest >= 0x807FFFFDu ||
        guest + offset < guest || guest + offset >= 0x80800000u) return 0xFFFFFFFFu;
    uint32_t p = guest + offset - 0x80000000u;
    return ((uint32_t)rdram[p] << 24) | ((uint32_t)rdram[p + 1] << 16) |
           ((uint32_t)rdram[p + 2] << 8) | rdram[p + 3];
}

static uint32_t rs64_m5_writer_state_byte(uint8_t* rdram, uint32_t guest,
                                           uint32_t offset) {
    if (guest < 0x80000000u || guest >= 0x80800000u ||
        guest + offset < guest || guest + offset >= 0x80800000u) return 0xFFFFFFFFu;
    return rdram[guest + offset - 0x80000000u];
}

static void rs64_m5_writer_state(uint8_t* rdram, recomp_context* ctx,
                                 uint32_t loop_v0, uint32_t target) {
    static int enabled = -1;
    static uint32_t bucket = 0xFFFFFFFFu;
    static unsigned controls = 0;
    static unsigned targets = 0;
    if (enabled < 0) {
        const char* all = getenv("ROGUESQ_LOG_ALL");
        const char* own = getenv("ROGUESQ_LOG_M5_WRITER_STATE");
        enabled = ((all && all[0] && all[0] != '0') ||
                   (own && own[0] && own[0] != '0')) ? 1 : 0;
    }
    if (!enabled) return;
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    extern uint32_t rs64_phase_ord(void);
    uint32_t width = rs64_vi_committed_width();
    uint32_t origin = rs64_vi_committed_origin() & 0x00FFFFFFu;
    if (!((width == 1024u && origin == 0x006AB800u) ||
          (width == 512u && origin == 0x006AB400u))) return;
    uint32_t key = (width << 24) ^ origin;
    if (key != bucket) {
        bucket = key;
        controls = 0;
        targets = 0;
    }
    unsigned* count = target ? &targets : &controls;
    unsigned limit = target ? 64u : 8u;
    if (*count >= limit) return;
    uint32_t s0 = U32(ctx->r16);
    uint32_t s1 = U32(ctx->r17);
    fprintf(stderr,
        "[m5-writer-state] n=%u target=%u phase=%u width=%u origin=0x%06X "
        "pc=0x800078EC ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X "
        "t0=0x%08X t1=0x%08X s0=0x%08X s1=0x%08X v0=0x%08X "
        "loop_v0=0x%08X v1=0x%08X pred=%u "
        "s0p60=0x%08X s0b22=0x%02X s1h22=0x%04X\n",
        *count, target, rs64_phase_ord(), width, origin, U32(ctx->r31),
        U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r8), U32(ctx->r9),
        s0, s1, U32(ctx->r2), loop_v0, U32(ctx->r3), target,
        rs64_m5_writer_state_word(rdram, s0, 0x60u),
        rs64_m5_writer_state_byte(rdram, s0, 0x22u),
        rs64_m5_writer_state_word(rdram, s1, 0x22u) & 0xFFFFu);
    fflush(stderr);
    ++*count;
}
'''


def main() -> None:
    text = GEN.read_text(encoding="utf-8")
    if MARKER in text:
        print("s3421 writer state already present")
        return
    include = '#include "funcs.h"\n'
    entry = "RECOMP_FUNC void rs_memset(uint8_t* rdram, recomp_context* ctx) {\n"
    store = "    rs64_probe_submit_gate_store('B', 0x800078ECu, U32(ADD32(ctx->r2, 0X0)), U32(ctx->r5));\n"
    if text.count(include) != 1 or text.count(entry) != 1 or text.count(store) != 1:
        raise SystemExit("s3421 writer state anchors are not unique")
    text = text.replace(include, include + HELPER + "\n", 1)
    text = text.replace(store, store + "    rs64_m5_writer_state(rdram, ctx, U32(ctx->r2), U32(U32(ctx->r2) >= 0x801797B0u && U32(ctx->r2) < 0x80179A48u)); /* PATCH: s3421 M5 writer-loop state */\n", 1)
    GEN.write_text(text, encoding="utf-8")
    print("s3421 writer state patched funcs_2.c")


if __name__ == "__main__":
    main()
