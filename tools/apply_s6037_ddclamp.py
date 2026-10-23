"""s6037 G1c: when ROGUESQ_DRAW_DISTANCE != 1, clamp the footprint window (0x80132DB0/B4/B8/BC, written at 0x80042944..0x800429BC
as min/ceil-max of the footprint polygon) to the terrain dims (u16 0x80136DF8 w, 0x80136DFA h). Retail never needs this because its
polygon stays inside the terrain; a scaled polygon spills past it (s6036 dd2: x0=3 w=33 on 32x32 -> getGridCellValueAt OOB, 5/5
SIGBUS). Updates $a3/$a2 (min x/z) too since the polygon is re-based on them. Retail (unset/1) = untouched. Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = "    // 0x800429C0: addu        $a1, $zero, $zero\n"
NEW = r'''    { /* PATCH: s6037 ddclamp */ static int on6037 = -1;
      if (on6037 < 0) { const char* e = getenv("ROGUESQ_DRAW_DISTANCE"); on6037 = (e && *e && atof(e) != 1.0) ? 1 : 0; }
      if (on6037) {
        int64_t h = (int64_t)(int32_t)0x80132000, t = (int64_t)(int32_t)0x80136000;
        int32_t tw = (int32_t)MEM_HU(0xDF8, t), th = (int32_t)MEM_HU(0xDFA, t);
        int32_t x0 = (int32_t)MEM_W(0xDB0, h), x1 = (int32_t)MEM_W(0xDB4, h), z0 = (int32_t)MEM_W(0xDB8, h), z1 = (int32_t)MEM_W(0xDBC, h);
        /* s6040: DB4/DBC are COUNTS (gridlog x0=20 w=37), not maxima; clamp [x0,x0+w) to terrain, then bound w*d by pool cap u16 0x80130C4C */
        { int32_t cap = (int32_t)MEM_HU(0xC4C, (int64_t)(int32_t)0x80130000);
          int32_t xl = x0 < 0 ? 0 : x0, xh = x0 + x1; if (xh > tw) xh = tw; x1 = xh > xl ? xh - xl : 0; x0 = xl;
          int32_t zl = z0 < 0 ? 0 : z0, zh = z0 + z1; if (zh > th) zh = th; z1 = zh > zl ? zh - zl : 0; z0 = zl;
          while (cap > 0 && x1 * z1 > cap && z1 > 1) z1--; while (cap > 0 && x1 * z1 > cap && x1 > 1) x1--; }
        MEM_W(0xDB0, h) = (uint32_t)x0; MEM_W(0xDB4, h) = (uint32_t)x1; MEM_W(0xDB8, h) = (uint32_t)z0; MEM_W(0xDBC, h) = (uint32_t)z1;
        ctx->r7 = (int64_t)x0; ctx->r6 = (int64_t)z0;
      } }
'''
def apply9(text):
    if "PATCH: s6037 ddclamp" in text or OLD not in text: return text, 0
    assert text.count(OLD) == 1
    return text.replace(OLD, NEW + OLD), 1
if __name__ == "__main__":
    p = base / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c live patched x%d" % n)
