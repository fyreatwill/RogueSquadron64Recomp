"""s6789 G3e: per-call reject reasons for streamTerrainGridCellsByDistance in the ROGUESQ_G3E_TRACE file (needs s6788 ddtrace).
After site 4 (same call), deltas of the s6493 exit counters since the previous call:
site 5 = (spaneq [4], r3-branch [5], r4-branch [6], poolcap row break [3]); site 6 = (zearly [1], xskip [2], nonode [9], bypass flips);
site 7 = (min d2, max d2 of kept nodes as float bits, kept-list head node, swap counter 0x80130C4C pool cap).
Bypass flips = cells the retail span compare rejected and the dd>1 bypass accepted when ROGUESQ_BYPASS_MAXCELLS<0. Idempotent."""
import pathlib
P = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
TAG = "/* s6789 rejtrace */"
F_OLD = "  if (cap < 0) return 1;\n  { static int rf6788 = 0;"
F_NEW = "  if (cap < 0) { g_s6789_flip++; return 1; } " + TAG + "\n  { static int rf6788 = 0;"
P_OLD = "void rs64_g3e_trace(unsigned site, unsigned a, unsigned b, unsigned c, unsigned d); int rs64_g3e_on(void); /* s6788 ddtrace */\n"
P_NEW = P_OLD + "static uint32_t g_s6789_flip; " + TAG + "\n"
S_OLD = "    // 0x80043A98: addu        $s0, $v0, $zero\n"
S_NEW = ("    if (rs64_g3e_on()) { static uint32_t pv[16], pf; uint32_t d[16]; int i; for (i = 0; i < 16; i++) { d[i] = g_s6493[i] - pv[i]; pv[i] = g_s6493[i]; } " + TAG + "\n"
         "      rs64_g3e_trace(5, d[4], d[5], d[6], d[3]); rs64_g3e_trace(6, d[1], d[2], d[9], g_s6789_flip - pf); pf = g_s6789_flip;\n"
         "      { uint32_t st = (uint32_t)ctx->r2, nd; int ps, n = 0; float mn = 1e30f, mx = -1e30f;\n"
         "        for (ps = 0; ps < 2; ps++) { nd = ps ? (st ? (uint32_t)MEM_W(0x4, (int64_t)(int32_t)st) : 0) : st; while (nd && n < 100000) { union { uint32_t u; float f; } c; c.u = (uint32_t)MEM_W(0x8, (int64_t)(int32_t)nd); if (c.f < mn) mn = c.f; if (c.f > mx) mx = c.f; n++; nd = (uint32_t)MEM_W(ps ? 0x4 : 0x0, (int64_t)(int32_t)nd); } }\n"
         "        { union { float f; uint32_t u; } a, b; a.f = mn; b.f = mx; rs64_g3e_trace(7, a.u, b.u, st, (uint32_t)rs64_swap_n()); } } }\n")
def apply9(t):
    if TAG in t: return t, 0
    assert t.count(F_OLD) == 1 and t.count(P_OLD) == 1 and t.count(S_OLD) == 1
    t = t.replace(P_OLD, P_NEW, 1).replace(F_OLD, F_NEW, 1).replace(S_OLD, S_NEW + S_OLD, 1)
    return t, 1
if __name__ == "__main__":
    t = P.read_text(); t2, n = apply9(t)
    if n: P.write_text(t2)
    print("funcs_9.c s6789 rejtrace x%d" % n)

# s6789b: pyramid inputs. site 8 = binPolygonIntoTerrainGrid's 5 grid-space points (i, x, y, z float bits) after the window clamp;
# site 9 = each scanConvertTriangleToSpanTable normal.y (float bits) with the two path thresholds (doubles 0x8003A4D0/D8 as float bits).
B_TAG = "/* s6789b pyramid */"
B1_OLD = "    // 0x800429C0: addu        $a1, $zero, $zero\n"
B1_NEW = ("    if (rs64_g3e_on()) { int i; for (i = 0; i < 5; i++) rs64_g3e_trace(8, (uint32_t)i, (uint32_t)MEM_W(i * 12, ctx->r4), (uint32_t)MEM_W(i * 12 + 4, ctx->r4), (uint32_t)MEM_W(i * 12 + 8, ctx->r4)); } " + B_TAG + "\n")
B2_OLD = "    // 0x80042388: lwc1        $f2, 0x34($sp)\n    ctx->f2.u32l = MEM_W(ctx->r29, 0X34);\n"
B2_NEW = ("    if (rs64_g3e_on()) { union { uint64_t u; double d; } lo, hi; union { float f; uint32_t u; } a, b; "
          "lo.u = ((uint64_t)(uint32_t)MEM_W(0, (int64_t)(int32_t)0x8003A4D0) << 32) | (uint32_t)MEM_W(4, (int64_t)(int32_t)0x8003A4D0); "
          "hi.u = ((uint64_t)(uint32_t)MEM_W(0, (int64_t)(int32_t)0x8003A4D8) << 32) | (uint32_t)MEM_W(4, (int64_t)(int32_t)0x8003A4D8); "
          "a.f = (float)lo.d; b.f = (float)hi.d; rs64_g3e_trace(9, ctx->f2.u32l, a.u, b.u, (uint32_t)ctx->r31); } " + B_TAG + "\n")
def applyb(t):
    if B_TAG in t: return t, 0
    assert t.count(B1_OLD) == 1 and t.count(B2_OLD) == 1
    return t.replace(B1_OLD, B1_NEW + B1_OLD, 1).replace(B2_OLD, B2_OLD + B2_NEW, 1), 1
if __name__ == "__main__":
    t = P.read_text(); t2, n = applyb(t)
    if n: P.write_text(t2)
    print("funcs_9.c s6789b pyramid x%d" % n)
