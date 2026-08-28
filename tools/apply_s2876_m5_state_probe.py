#!/usr/bin/env python3
"""Regeneration-safe probe for the retail state-arbiter store."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT.parent / "N64Recomp" / "RecompiledFuncs" / "funcs_17.c"
MARK = "/* fixup: s2876 m5 state-arbiter probe */"
HELPER = r'''
static void rs64_s2876_state_store(uint8_t* rdram, uint32_t pc,
                                   uint32_t addr, uint32_t value) {
    static int enabled = -1;
    static unsigned long rows = 0;
    if (enabled < 0) {
        const char* e = getenv("ROGUESQ_LOG_M5_STATE_ARBITER");
        enabled = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    if (!enabled) return;
    extern uint32_t rs64_phase_ord(void);
    uint32_t phase = rs64_phase_ord();
    if (phase < 4 || rows >= 256) return;
    uint32_t phys = (addr & 0x1FFFFFFFu) - 0x10u;
    fprintf(stderr, "[m5-state-control] phase=%u pc=0x%08X addr=0x%08X value=0x%08X\n",
            phase, pc, addr, value);
    fprintf(stderr, "[m5-state-span] phase=%u pc=0x%08X base=0x%08X bytes=",
            phase, pc, phys);
    for (unsigned i = 0; i < 0x40; ++i) fprintf(stderr, "%02X", rdram[phys + i]);
    fputc('\n', stderr);
    fflush(stderr);
    ++rows;
}
'''
text = GEN.read_text()
if MARK not in text:
    anchor = "static int s_process_scene_node_depth;\n"
    text = text.replace(anchor, HELPER + "\n" + anchor, 1)
needle = "        rs64_probe_submit_gate_store('W', 0x8006E4B4u, U32(ADD32(ctx->r16, 0X10)), U32(ctx->r2));"
replacement = needle + "\n        rs64_s2876_state_store(rdram, 0x8006E4B4u, U32(ADD32(ctx->r16, 0X10)), U32(ctx->r2)); " + MARK
text = text.replace(needle, replacement)
GEN.write_text(text)
print("patched", GEN)
