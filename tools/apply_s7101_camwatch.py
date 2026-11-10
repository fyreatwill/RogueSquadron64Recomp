"""s7101 fps60-wall-camera: write-watch on the flight camera matrix, to name the store that zig-zags the eye at the
FPS60 near-wall flicker (s7100 H-push).

The terrain builder (buildVisibleTerrainGridAroundCamera 0x800437B0) reads its eye from the 3x4 matrix at
cam = *(u32*)0x80138D1C, + 0x28 (rotation 9 floats, translation at +0x4C/+0x50/+0x54) and writes the scaled copy to
0x80130C10 (the [g3c] eye). This hooks every generated guest store (the s5798 per-store macro; needs g_rs64_store_diag,
so set ROGUESQ_STORE_DIAG=1) into [cam, cam+0x58) (s7101b: widened from cam+0x28 to catch the chase state at +0x10..0x18) and into the pointer word 0x80138D1C itself.

Env ROGUESQ_S7101_CAMW=<path>: one text line per store
  m=<mach_absolute_time> lim=<0x80128EAF> fc=<frame counter 0x8011A890> pc=<store pc> ra=<guest ra> fn=<func> off=<0x28..0x54> v=<float>
and a `ptr` line on each 0x80138D1C store. Positive control: the ordinary per-tick camera update must appear on every
tick in flight (stores to off 0x4C/0x50/0x54 at ~60/s in lim=1 windows). Blind to host writers (memcpy/DMA/C patches).
Measurement only: no game value is changed. Idempotent; mirrored in fixup_game_funcs_vendored.py's apply list."""
from pathlib import Path
import re
D = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7101 camwatch"
n = 0
for p in sorted(D.glob("funcs_*.c")):
    t = p.read_text()
    if "#define RS64_S5798_ST" not in t or MARK in t:
        continue
    new, k = re.subn(r"(_a5798 = \(uint32_t\)\(\(base\) \+ \(off\)\); if \()",
                     r"\1(uint32_t)(_a5798 - g_rs64_s7101_lo) < 0x58u || _a5798 == 0x80138D1Cu || ", t, count=1)
    if k:
        new = new.replace("#define RS64_S5798_ST", "/* " + MARK + " */\nextern uint32_t g_rs64_s7101_lo;\n#define RS64_S5798_ST", 1)
        p.write_text(new); n += 1
print("s7101 macro patched in", n, "files")
P = D / "funcs_13.c"
T = P.read_text()
helper = r'''/* PATCH: s7101 camwatch helper */
#include <mach/mach_time.h>
uint32_t g_rs64_s7101_lo = 0x80138458u; /* flight camera (s5080) until the pointer store is seen; watch [cam, cam+0x58) */
static FILE* s7101_f(void) {
    static int st = -1; static FILE* f = NULL;
    if (st < 0) { const char* e = getenv("ROGUESQ_S7101_CAMW"); st = 0;
        if (e && e[0] && e[0] != '0') { f = fopen(e, "w"); if (f) { static char buf[1 << 20]; setvbuf(f, buf, _IOFBF, sizeof buf); st = 1; } } }
    return st ? f : NULL;
}
static void s7101_note(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {
    FILE* f = s7101_f(); if (!f) return;
    unsigned long long m = (unsigned long long)mach_absolute_time();
    if (a == 0x80138D1Cu) {
        uint32_t v = (uint32_t)MEM_W(0, (gpr)(int32_t)0x80138D1Cu);
        if (v >= 0x80000000u && v < 0x80800000u) g_rs64_s7101_lo = v;
        fprintf(f, "ptr m=%llu pc=%08X fn=%s v=%08X\n", m, pc, fn, v);
        return;
    }
    uint32_t aw = a & ~3u, u = (uint32_t)MEM_W(0, (gpr)(int32_t)aw); float fv; memcpy(&fv, &u, 4);
    fprintf(f, "st m=%llu lim=%u fc=%u pc=%08X ra=%08X fn=%s off=%02X w=%d v=%.6g\n", m, (unsigned)MEM_BU(0, (gpr)(int32_t)0x80128EAFu),
            (uint32_t)MEM_W(0, (gpr)(int32_t)0x8011A890u), pc, (uint32_t)ctx->r31, fn, aw - g_rs64_s7101_lo, w, (double)fv);
    if (w == 8) { uint32_t u2 = (uint32_t)MEM_W(0, (gpr)(int32_t)(aw + 4)); float f2; memcpy(&f2, &u2, 4);
        fprintf(f, "st m=%llu lim=%u fc=%u pc=%08X ra=%08X fn=%s off=%02X w=8b v=%.6g\n", m, (unsigned)MEM_BU(0, (gpr)(int32_t)0x80128EAFu),
                (uint32_t)MEM_W(0, (gpr)(int32_t)0x8011A890u), pc, (uint32_t)ctx->r31, fn, aw + 4 - g_rs64_s7101_lo, (double)f2); }
}
'''
anchor = "void rs64_s5798_st(uint8_t* rdram, recomp_context* ctx, uint32_t pc, uint32_t a, int w, const char* fn) {\n"
assert T.count(anchor) == 1
if "s7101_note" in T:
    print("s7101 handler already present")
else:
    T = T.replace(anchor, helper + anchor + "    if (a == 0x80138D1Cu || (uint32_t)(a - g_rs64_s7101_lo) < 0x58u) { s7101_note(rdram, ctx, pc, a, w, fn); return; } /* " + MARK + " */\n", 1)
    P.write_text(T); print("s7101 handler added")
