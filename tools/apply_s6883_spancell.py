#!/usr/bin/env python3
"""s6883 G1d/G1c: span scan edge rows past 80 get real storage, span cells get a real 64x64 bound, default on inside dd != 1 or wide.
scanConvertTriangleToSpanTable keeps its edges in min 0x80130C70 and max 0x80130D10, 80 rows each, and the two walkers write them with no limit. Rows past 80 land: min on max,
max on the first span table (0x80130DB0). The s6049/s6880 bound keeps stores inside the 0x2000 of both tables, so row >= 64 of table 1 and row < 0 of table 2 land in the OTHER
table, and x outside 0..63 lands in the next or previous row. ROGUESQ_G1D_SPANCELL bits: 1 = edge rows >= 80 go to host arrays, 2 = cells outside 64x64 dropped, 4 = control,
blank rows 20..23 of both tables. Default 3 where the s6882 gate runs, =0 old. ROGUESQ_G1D_SPANLOG=1 logs [spancell]; ROGUESQ_G1D_SPANDUMP=<prefix> writes the tables at each POSE_FREEZE.
All hooks run only where rs64_s6882_on() holds, so retail dd1 4:3 is untouched. Runs after apply_s6882_spannarrow in RS64_REPLAY. Idempotent.
Usage: apply_s6883_spancell.py [RecompiledFuncs dir]
"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6883 spancell"
MIN_ST = ("0x80042038", "0x80042068", "0x800420B4", "0x80042100")
MAX_ST = ("0x800421B0", "0x80042200", "0x8004225C", "0x80042288")
LOADS = (("0x80042080", 0), ("0x8004217C", 1))
HEAD = "RECOMP_FUNC void streamTerrainGridCellsByDistance(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n"
N82 = "    { /* PATCH: s6882 spannarrow */"
ROW = ("    { /* " + TAG + " */ extern void rs64_s6883_row(uint32_t, int32_t, int32_t, int64_t*, int64_t*); if (rs64_s6882_on()) { int64_t a6883 = (int32_t)ctx->r4, b6883 = (int32_t)ctx->r6;\n"
       "      rs64_s6883_row(U32(ctx->r7), (int32_t)ctx->r5, (int32_t)ctx->r12, &a6883, &b6883); ctx->r4 = (gpr)a6883; ctx->r6 = (gpr)b6883; } }\n")

def apply9(text):
    if TAG in text: return text, 0
    n = 0
    for sites, w, lim in ((MIN_ST, 0, "0x80130D10u"), (MAX_ST, 1, "0x80130DB0u")):
        for pc in sites:
            a = "{ MEM_H(0X0, ctx->r3) = ctx->r2; RS64_S5798_ST(%su, 0X0, ctx->r3, 2); }" % pc
            assert text.count(a) >= 1, "s6883 store " + pc
            b = ("{ /* %s */ extern int rs64_s6883_edge(int, uint32_t, int32_t); if (!(U32(ctx->r3) >= %s && rs64_s6883_edge(%d, U32(ctx->r3), (int32_t)ctx->r2))) "
                 "{ MEM_H(0X0, ctx->r3) = ctx->r2; RS64_S5798_ST(%su, 0X0, ctx->r3, 2); } }") % (TAG, lim, w, pc)
            n += text.count(a); text = text.replace(a, b)
    for pc, w in LOADS:
        a = "    // %s: lh          $v0, 0x0($v0)\n    ctx->r2 = MEM_H(ctx->r2, 0X0);\n" % pc
        assert text.count(a) >= 1, "s6883 load " + pc
        b = ("    // %s: lh          $v0, 0x0($v0)\n    { /* %s */ extern int rs64_s6883_edgerd(int, uint32_t, int32_t*); int32_t v6883; "
             "if (rs64_s6883_edgerd(%d, U32(ctx->r2), &v6883)) ctx->r2 = (gpr)(int64_t)v6883; else ctx->r2 = MEM_H(ctx->r2, 0X0); }\n") % (pc, TAG, w)
        n += text.count(a); text = text.replace(a, b)
    assert text.count(N82) == 2, "s6883 needs s6882 text"
    text = text.replace(N82, ROW + N82); n += 2
    assert text.count(HEAD) == 1, "s6883 stream head"
    text = text.replace(HEAD, HEAD + "    { /* %s */ extern void rs64_s6883_tables(uint8_t*); rs64_s6883_tables(rdram); }\n" % TAG); n += 1
    return text, n

if __name__ == "__main__":
    p = D / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c s6883 spancell x%d" % n)
