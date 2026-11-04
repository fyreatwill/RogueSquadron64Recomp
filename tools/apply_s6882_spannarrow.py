#!/usr/bin/env python3
"""s6882 G1d/G1c: narrow the x range of the two span fill loops in scanConvertTriangleToSpanTable to the stores the s6049/s6880 bound would keep.
The edge walkers 0x80041FA4 / 0x80042118 write row i of the min (0x80130C70) and max (0x80130D10) arrays with no limit. Each array holds 80 rows, so a footprint deeper
than that reads max[i >= 80] from the span table at 0x80130DB0: 0x7F7F = 32639, and each such row walks x up to 32639 with three float divides per x, every store skipped.
h219d4 s6882: 3.84e9 skips in 130 s. Retail cannot reach it; dd > 1 and wide frames do. Narrowing drops only iterations whose store the bound already skips: each iteration
stands alone, so the stored bytes are the same. Runs only where the bound runs (dd != 1 or a wide frame). ROGUESQ_G1D_SPANNARROW=0 = old.
Runs after apply_s6880_widebound in RS64_REPLAY. Idempotent.  Usage: apply_s6882_spannarrow.py [RecompiledFuncs dir]
"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6882 spannarrow"
INS = ("    { /* " + TAG + " */ extern int rs64_s6882_on(void); if (rs64_s6882_on()) { const int64_t rel = (int64_t)(int32_t)ctx->r12 + ((int64_t)(int32_t)ctx->r5 << 6) - (int64_t)(int32_t)0x80130DB0;\n"
       "      if ((int64_t)(int32_t)ctx->r4 < -rel) ctx->r4 = (gpr)(-rel); if ((int64_t)(int32_t)ctx->r6 > 0x1FFF - rel) ctx->r6 = (gpr)(0x1FFF - rel); } }\n")
def apply9(text):
    if TAG in text: return text, 0
    n = 0
    for pc in ("0x80042600", "0x80042748"):
        a = "    // %s: slt         $v0, $a2, $a0\n" % pc
        assert text.count(a) == 1, "s6882 anchor " + pc
        text = text.replace(a, INS + a); n += 1
    return text, n

if __name__ == "__main__":
    p = D / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c s6882 spannarrow x%d" % n)
