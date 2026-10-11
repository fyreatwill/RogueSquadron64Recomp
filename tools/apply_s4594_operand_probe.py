#!/usr/bin/env python3
"""Add the phase-gated s4594 operand census at fillSampleStreamRange's subtraction."""
from pathlib import Path

p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c")
s = p.read_text()
if "rs64_s4594_operand" in s:
    print("already applied")
    raise SystemExit(0)

helper = r'''
/* PATCH: s4594 phase-gated operand census. Diagnostic only. */
static void rs64_s4594_operand(uint8_t* rdram, uint32_t node, uint32_t a1,
                               uint32_t a2, uint32_t a3, uint32_t computed) {
    static int on = -1;
    static uint32_t phase_seen = 0xFFFFFFFFu;
    static unsigned bad_rows = 0, ctl_rows = 0;
    if (on < 0) {
        const char* e = getenv("ROGUESQ_LOG_S4594");
        on = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    if (!on) return;
    extern uint32_t rs64_phase_ord(void);
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    const uint32_t phase = rs64_phase_ord();
    const uint32_t width = rs64_vi_committed_width();
    const uint32_t origin = rs64_vi_committed_origin();
    if (width != 640u || origin != 0x006A2900u) return;
    if (phase_seen != phase) { phase_seen = phase; bad_rows = 0; ctl_rows = 0; }
    const uint32_t n0 = (uint32_t)MEM_W(0, S32(node));
    const uint32_t n4 = (uint32_t)MEM_W(4, S32(node));
    const uint32_t n8 = (uint32_t)MEM_W(8, S32(node));
    const uint32_t nc = (uint32_t)MEM_W(0xC, S32(node));
    const uint32_t n10 = (uint32_t)MEM_W(0x10, S32(node));
    const uint32_t n14 = (uint32_t)MEM_W(0x14, S32(node));
    const uint32_t head = (uint32_t)MEM_W(-0x661C, S32(0x8015 << 16));
    const uint32_t tail = (uint32_t)MEM_W(-0x664C, S32(0x8015 << 16));
    const uint32_t pool = (uint32_t)MEM_W(-0x6634, S32(0x8015 << 16));
    const uint32_t top = computed >> 24;
    const int bad = (computed & 1u) || (top >= 0x20u && top < 0x7Fu);
    if (bad) {
        if (bad_rows++ >= 12) return;
    } else {
        if (ctl_rows++ >= 4) return;
    }
    fprintf(stderr,
        "[s4594-operand] kind=%s phase=%u width=%u origin=0x%06X node=%08X a1=%08X a2=%08X a3=%08X computed=%08X n0=%08X n4=%08X n8=%08X nC=%08X n10=%08X n14=%08X head=%08X tail=%08X pool=%08X\n",
        bad ? "bad" : "control", phase, width, origin, node, a1, a2, a3,
        computed, n0, n4, n8, nc, n10, n14, head, tail, pool);
    fflush(stderr);
}

'''

anchor = "RECOMP_FUNC void fillSampleStreamRange(uint8_t* rdram, recomp_context* ctx) {\n"
if s.count(anchor) != 1:
    raise SystemExit(f"function anchor count {s.count(anchor)}")
s = s.replace(anchor, helper + anchor +
              "    const uint32_t s4594_a1 = U32(ctx->r5);\n"
              "    const uint32_t s4594_a2 = U32(ctx->r6);\n"
              "    const uint32_t s4594_a3 = U32(ctx->r7);\n", 1)

anchor = "    // 0x8008FDC0: sw          $v0, 0x8($t0)\n"
call = ("    rs64_s4594_operand(rdram, U32(ctx->r8), s4594_a1, s4594_a2, "
        "s4594_a3, U32(ctx->r2)); /* PATCH: s4594 */\n")
if s.count(anchor) != 1:
    raise SystemExit(f"store anchor count {s.count(anchor)}")
s = s.replace(anchor, anchor + call, 1)
p.write_text(s)
print("applied")
