"""s6037 G1c: when ROGUESQ_DRAW_DISTANCE != 1, clamp the footprint window (0x80132DB0/B4/B8/BC, written at 0x80042944..0x800429BC
as min/ceil-max of the footprint polygon) to the terrain dims (u16 0x80136DF8 w, 0x80136DFA h). Retail never needs this because its
polygon stays inside the terrain; a scaled polygon spills past it (s6036 dd2: x0=3 w=33 on 32x32 -> getGridCellValueAt OOB, 5/5
SIGBUS). Updates $a3/$a2 (min x/z) too since the polygon is re-based on them. Retail (unset/1) = untouched. Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = "    // 0x800429C0: addu        $a1, $zero, $zero\n"
NEW = r'''    { /* PATCH: s6037 ddclamp */ static int on6037 = -1;
      if (on6037 < 0) { const char* e = getenv("ROGUESQ_DRAW_DISTANCE"); on6037 = (e && *e && atof(e) != 1.0) ? 1 : 0; }
      if (on6037 && MEM_W(4, (int64_t)(int32_t)0x80136DC0) != 0) {
        int64_t h = (int64_t)(int32_t)0x80132000, t = (int64_t)(int32_t)0x80136000;
        int32_t tw = (int32_t)MEM_HU(0xDF8, t), th = (int32_t)MEM_HU(0xDFA, t);
        int32_t x0 = (int32_t)MEM_W(0xDB0, h), x1 = (int32_t)MEM_W(0xDB4, h), z0 = (int32_t)MEM_W(0xDB8, h), z1 = (int32_t)MEM_W(0xDBC, h);
        /* s6053: at this point DB4/DBC are still EXCLUSIVE MAXIMA (ceil of polygon max); 0x80042A30 later does DB4-=DB0, DBC-=DB8 to make counts.
           s6040 clamped them as counts, so DB4=tw-x0 then lost x0 again at 2A30 -> negative u32-wrapped counts (s6052 w=4294967286). Clamp as maxima. */
        { int32_t cap = (int32_t)MEM_HU(0xC4C, (int64_t)(int32_t)0x80130000);
          /* s6548 log */ static int n6548 = 0; int32_t px0 = x0, px1 = x1, pz0 = z0, pz1 = z1;
          if (x0 < 0) x0 = 0; if (x1 > tw) x1 = tw; if (x1 < x0) x1 = x0;
          if (z0 < 0) z0 = 0; if (z1 > th) z1 = th; if (z1 < z0) z1 = z0;
          while (cap > 0 && (x1 - x0) * (z1 - z0) > cap && (z1 - z0) > 1) z1--; while (cap > 0 && (x1 - x0) * (z1 - z0) > cap && (x1 - x0) > 1) x1--;
          if (getenv("ROGUESQ_DD_LOG") && (n6548++ % 60) == 0) fprintf(stderr, "[ddclamp] pre x[%d,%d) z[%d,%d) tw=%d th=%d cap=%d post x[%d,%d) z[%d,%d)\n", px0, px1, pz0, pz1, tw, th, cap, x0, x1, z0, z1); }
        MEM_W(0xDB0, h) = (uint32_t)x0; MEM_W(0xDB4, h) = (uint32_t)x1; MEM_W(0xDB8, h) = (uint32_t)z0; MEM_W(0xDBC, h) = (uint32_t)z1;
        ctx->r7 = (int64_t)x0; ctx->r6 = (int64_t)z0;
      } }
'''
def apply9(text):
    if "PATCH: s6037 ddclamp" in text and "s6548 log" in text or OLD not in text: return text, 0
    if "PATCH: s6037 ddclamp" in text:
        i = text.index("    { /* PATCH: s6037 ddclamp */"); j = text.index(OLD, i); text = text[:i] + text[j:]
    assert text.count(OLD) == 1
    return text.replace(OLD, NEW + OLD), 1
if __name__ == "__main__":
    p = base / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c live patched x%d" % n)
