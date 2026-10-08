#!/usr/bin/env python3
"""s4223: dump the stack buffer sp+0x18..0x8C of the function at 0x800A64BC..0x800A6568 (filled by 0x800AF60C) at
pre-call (64CC), post-call (64D4), post-shutdown calls (64FC) and just before the volume-byte read (6520).
Retail twin: scratch/agent/run_s4223_retail_stk.sh (RS64_STACK_DUMP_PCS). Env ROGUESQ_LOG_S4223=1. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s4223 stk"
CODE = r'''
extern "C" void rs64_s4223_stk(uint8_t* rdram, uint32_t pc, uint32_t sp, uint32_t v0) {
    static const bool on = [] { const char* e = std::getenv("ROGUESQ_LOG_S4223"); return e && e[0] && e[0] != '0'; }();
    if (!rdram || !on) return;
    static int n = 0; if (++n > 64) return;
    std::fprintf(stderr, "[s4223-stk] pc=%08X sp=%08X v0=%08X stk=", pc, sp, v0);
    for (uint32_t o = 0x18; o < 0x90; o += 4) {
        const uint32_t a = (sp + o) & 0x1FFFFFFFu;
        const uint32_t w = (uint32_t(rdram[(a + 0) ^ 3]) << 24) | (uint32_t(rdram[(a + 1) ^ 3]) << 16) | (uint32_t(rdram[(a + 2) ^ 3]) << 8) | rdram[(a + 3) ^ 3];
        std::fprintf(stderr, "%08x,", w);
    }
    std::fprintf(stderr, "\n");
}
'''
SITES = [("    // 0x800A64CC: jal         0x800AF60C\n", 0x800A64CC, "before"),
         ("    after_52:\n", 0x800A64D4, "after"),
         ("    after_56:\n", 0x800A64FC, "after"),
         ("    // 0x800A6520: lbu         $t0, 0x88($sp)\n", 0x800A6520, "before")]
def patch_cpp():
    f = R / "src/main/upstream_compat.cpp"
    t = f.read_text()
    if "rs64_s4223_stk" in t: return
    anchor = 'extern "C" void rs64_m5_voice_modulation_call(uint8_t* rdram, uint32_t pc,'
    assert t.count(anchor) == 1
    f.write_text(t.replace(anchor, CODE + anchor))
def patch_c():
    p = RF / "funcs_27.c"
    s = p.read_text()
    if MARK in s: return
    for anchor, pc, where in SITES:
        assert s.count(anchor) >= 1, anchor
        call = f"    rs64_s4223_stk(rdram, 0x{pc:08X}u, U32(ctx->r29), U32(ctx->r2)); /* {MARK} */\n"
        base = s.index("L_800A64BC:")
        i = s.index(anchor, base)
        s = s[:i] + ((call + anchor) if where == "before" else (anchor + call)) + s[i + len(anchor):]
    a = '#include "funcs.h"\n'
    s = s.replace(a, a + "extern void rs64_s4223_stk(uint8_t*, uint32_t, uint32_t, uint32_t);\n", 1)
    p.write_text(s)
if __name__ == "__main__":
    patch_cpp(); patch_c(); print("ok")
