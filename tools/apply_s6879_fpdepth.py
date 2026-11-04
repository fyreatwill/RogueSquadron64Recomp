#!/usr/bin/env python3
"""s6879 G1d: 16:9 flight lost far terrain that 4:3 draws at the same pose (hills gone behind the craft, ragged plain horizon).
ORIGIN: our own s6144 footprint widening. buildVisibleTerrainGridAroundCamera multiplies the corner x by k at 0x800438C4, then
0x80043930 calls the normalize at 0x8001CF58 and scales to a fixed length (0x8009DEB0), so a wider x comes at the expense of y and
z: the pyramid's forward reach shrinks and only the sides gain. Retail's value there is legitimate; the widening was misplaced.
Fix: after the length scale, restore the length the corner would have had, r = |v| / |(x/k, y, z)|, so y and z equal the 4:3
corner and only x is k wider. k = 1 (4:3, 640 states) skips the block: bit-identical retail. ROGUESQ_G1D_FPDEPTH=0 = old.
Runs after apply_s6144_fpx. Idempotent.  Usage: apply_s6879_fpdepth.py [RecompiledFuncs dir]
"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
K_OLD = "      if (k6719 != 1.0) { union"
K_NEW = "      { extern double rs64_s6879_fpk; rs64_s6879_fpk = k6719; } /* PATCH: s6879 fpk */\n" + K_OLD
OLD = "    // 0x8004395C: swc1        $f6, 0x40($sp)\n"
NEW = r'''    { /* PATCH: s6879 fpdepth */ extern double rs64_s6879_fpk; static int on6879 = -1; const double k = rs64_s6879_fpk;
      if (on6879 < 0) { const char* e = getenv("ROGUESQ_G1D_FPDEPTH"); on6879 = !(e && *e == '0'); }
      if (on6879 && k != 1.0) { union { uint32_t u; float f; } x, y, z; x.u = ctx->f6.u32l; y.u = ctx->f4.u32l; z.u = ctx->f2.u32l;
        const double yz = (double)y.f * y.f + (double)z.f * z.f, xx = (double)x.f * x.f, r = __builtin_sqrt((xx + yz) / (xx / (k * k) + yz));
        x.f = (float)(x.f * r); y.f = (float)(y.f * r); z.f = (float)(z.f * r); ctx->f6.u32l = x.u; ctx->f4.u32l = y.u; ctx->f2.u32l = z.u; } }
'''
def apply9(text):
    if "PATCH: s6879 fpdepth" in text: return text, 0
    assert text.count(K_OLD) == 1 and text.count(OLD) == 1, "s6879 anchors"
    return text.replace(K_OLD, K_NEW).replace(OLD, NEW + OLD), 1

if __name__ == "__main__":
    p = D / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c s6879 fpdepth x%d" % n)
