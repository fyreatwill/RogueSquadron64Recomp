"""s6788 G3e: ROGUESQ_G3E_TRACE=<file> per-call terrain trace for the draw-distance path (funcs_9.c), one line per event via
rs64_g3e_trace (src/rsp/dpc_bridge.cpp, stamped with VI + swap): site 1 = s6036 radius read (dd applied?, desc+4 word, radius
after scaling), site 2 = s6037 post-clamp window (x0 x1 z0 z1), site 3 = s6537 bypass cap per swap (swap, taken, refused at cap),
site 4 = after streamTerrainGridCellsByDistance (kept nodes, window cells, pool cap). Unset = no output. Idempotent."""
import pathlib
P = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
TAG = "/* s6788 ddtrace */"
PROTO = "void rs64_g3e_trace(unsigned site, unsigned a, unsigned b, unsigned c, unsigned d); int rs64_g3e_on(void); " + TAG + "\n"
S1_OLD = "      if (me6036 != 1.0f && MEM_W(4, (int64_t)(int32_t)0x80136DC0) != 0) { union { uint32_t u; float f; } c; c.u = ctx->f2.u32l; c.f *= me6036; ctx->f2.u32l = c.u; }"
S1_NEW = S1_OLD + " if (rs64_g3e_on()) rs64_g3e_trace(1, me6036 != 1.0f, (uint32_t)MEM_W(4, (int64_t)(int32_t)0x80136DC0), ctx->f2.u32l, 0); " + TAG
S2_OLD = "        MEM_W(0xDB0, h) = (uint32_t)x0; MEM_W(0xDB4, h) = (uint32_t)x1; MEM_W(0xDB8, h) = (uint32_t)z0; MEM_W(0xDBC, h) = (uint32_t)z1;\n"
S2_NEW = S2_OLD + "        if (rs64_g3e_on()) rs64_g3e_trace(2, (uint32_t)x0, (uint32_t)x1, (uint32_t)z0, (uint32_t)z1); " + TAG + "\n"
S3_OLD = "  if (n != lastn) { lastn = n; used = 0; }\n  if (used >= cap) return 0; used++; return 1; }\n"
S3_NEW = ("  { static int rf6788 = 0; if (n != lastn) { if (lastn >= 0 && rs64_g3e_on()) rs64_g3e_trace(3, (uint32_t)lastn, (uint32_t)used, (uint32_t)rf6788, (uint32_t)cap); lastn = n; used = 0; rf6788 = 0; } " + TAG + "\n"
          "  if (used >= cap) { rf6788++; return 0; } used++; return 1; } }\n")
S4_OLD = "    // 0x80043A98: addu        $s0, $v0, $zero\n"
S4_NEW = ("    if (rs64_g3e_on()) { uint32_t nd = (uint32_t)ctx->r2, st = nd; int kept = 0, ps; " + TAG + "\n"
          "      for (ps = 0; ps < 2; ps++) { nd = ps ? (st ? (uint32_t)MEM_W(0x4, (int64_t)(int32_t)st) : 0) : st; while (nd && kept < 100000) { kept++; nd = (uint32_t)MEM_W(ps ? 0x4 : 0x0, (int64_t)(int32_t)nd); } }\n"
          "      { int64_t h = (int64_t)(int32_t)0x80132000; rs64_g3e_trace(4, (uint32_t)kept, (uint32_t)MEM_W(0xDB4, h) * (uint32_t)MEM_W(0xDBC, h), (uint32_t)MEM_HU(0xC4C, (int64_t)(int32_t)0x80130000), (uint32_t)MEM_W(0xDB0, h) | ((uint32_t)MEM_W(0xDB8, h) << 16)); } }\n")
def apply9(t):
    if TAG in t: return t, 0
    for o in (S1_OLD, S2_OLD, S3_OLD): assert t.count(o) == 1, o[:60]
    assert t.count(S4_OLD) == 1
    i = t.index("static inline int s6537_take(void)")
    t = t[:i] + PROTO + t[i:]
    t = t.replace(S1_OLD, S1_NEW, 1).replace(S2_OLD, S2_NEW, 1).replace(S3_OLD, S3_NEW, 1).replace(S4_OLD, S4_NEW + S4_OLD, 1)
    return t, 1
if __name__ == "__main__":
    t = P.read_text(); t2, n = apply9(t)
    if n: P.write_text(t2)
    print("funcs_9.c s6788 ddtrace x%d" % n)
