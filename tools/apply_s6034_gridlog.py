"""s6034 G1c: ROGUESQ_DD_GRIDLOG=1 logs, after each streamTerrainGridCellsByDistance call in buildVisibleTerrainGridAroundCamera
(funcs_9.c, 0x80043A98): window (0x80132DB0/B4/B8/BC), terrain w/h (0x80136DF8/FA), pool cap (u16 0x80130C4C), kept node count
(walk list from $v0 via +0), min/max node dist^2 (+8) and max grid x/z (+0xC/+0x10). Default unset = no output. Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = "    after_10:\n    // 0x80043A98: addu        $s0, $v0, $zero\n"
NEW = r'''    { /* PATCH: s6034 gridlog */ static int on6034 = -1; static int n6034 = 0;
      if (on6034 < 0) { const char* e = getenv("ROGUESQ_DD_GRIDLOG"); on6034 = (e && *e && *e != '0') ? 1 : 0; }
      if (on6034 && (n6034++ % 30) == 0) {
        int64_t g = (int64_t)(int32_t)0x80130000, h = (int64_t)(int32_t)0x80132000, t = (int64_t)(int32_t)0x80136000;
        uint32_t cap = (uint32_t)MEM_HU(0xC4C, g), wx = (uint32_t)MEM_W(0xDB0, h), ww = (uint32_t)MEM_W(0xDB4, h), wz = (uint32_t)MEM_W(0xDB8, h), wd = (uint32_t)MEM_W(0xDBC, h);
        uint32_t tw = (uint32_t)MEM_HU(0xDF8, t), th = (uint32_t)MEM_HU(0xDFA, t);
        uint32_t node = (uint32_t)ctx->r2; int kept = 0; float dmin = 1e30f, dmax = -1.0f; int32_t xmax = -999999, zmax = -999999, xmin = 999999, zmin = 999999;
        /* s6056: list is doubly linked (next +0, prev +4); v0 is not an end, so walk both ways (old forward-only walk always gave kept=1) */
        uint32_t start6056 = node; int pass6056;
        for (pass6056 = 0; pass6056 < 2; pass6056++) { node = start6056; if (pass6056) node = node ? (uint32_t)MEM_W(0x4, (int64_t)(int32_t)node) : 0;
        while (node && kept < 100000) { int64_t nb = (int64_t)(int32_t)node; union { uint32_t u; float f; } d; d.u = (uint32_t)MEM_W(0x8, nb);
          if (d.f < dmin) dmin = d.f; if (d.f > dmax) dmax = d.f; int32_t gx = (int32_t)MEM_W(0xC, nb), gz = (int32_t)MEM_W(0x10, nb);
          if (gx > xmax) xmax = gx; if (gx < xmin) xmin = gx; if (gz > zmax) zmax = gz; if (gz < zmin) zmin = gz; kept++; node = (uint32_t)MEM_W(pass6056 ? 0x4 : 0x0, nb); } }
        fprintf(stderr, "[gridlog] win x0=%u w=%u z0=%u d=%u req=%u terr=%ux%u cap=%u kept=%d d2[min=%.1f max=%.1f] gx[%d..%d] gz[%d..%d]\n", wx, ww, wz, wd, ww * wd, tw, th, cap, kept, dmin, dmax, xmin, xmax, zmin, zmax);
      } }
'''
def apply9(text):
    if "PATCH: s6034 gridlog" in text or OLD not in text: return text, 0
    assert text.count(OLD) == 1
    return text.replace(OLD, OLD.replace("    after_10:\n", "    after_10:\n" + NEW)), 1
if __name__ == "__main__":
    p = base / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c live patched x%d" % n)
