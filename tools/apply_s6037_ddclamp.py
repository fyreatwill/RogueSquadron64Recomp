"""s6037 G1c: when ROGUESQ_DRAW_DISTANCE != 1, clamp the footprint window (0x80132DB0/B4/B8/BC, written at 0x80042944..0x800429BC
as min/ceil-max of the footprint polygon) to the terrain dims (u16 0x80136DF8 w, 0x80136DFA h). Retail never needs this because its
polygon stays inside the terrain; a scaled polygon spills past it (s6036 dd2: x0=3 w=33 on 32x32 -> getGridCellValueAt OOB, 5/5
SIGBUS; that SIGBUS was the span table, s6049/s6591 bound it, and s6874 stopped clamping to the dims). Updates $a3/$a2 (min x/z) too since the polygon is re-based on them. Retail (unset/1) = untouched. Idempotent."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = "    // 0x800429C0: addu        $a1, $zero, $zero\n"
NEW = r'''    { /* s6590 desc log */ static int dl = -1, dn = 0; if (dl < 0) dl = getenv("ROGUESQ_TBLNULL_LOG") ? 1 : 0;
      if (dl && (dn++ % 300) == 0 && dn < 3000) fprintf(stderr, "[desc6590] call=%d w0=%08X w4=%08X w8=%08X wC=%08X tw=%u th=%u\\n", dn, (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80136DC0), (uint32_t)MEM_W(4, (int64_t)(int32_t)0x80136DC0), (uint32_t)MEM_W(8, (int64_t)(int32_t)0x80136DC0), (uint32_t)MEM_W(0xC, (int64_t)(int32_t)0x80136DC0), (unsigned)MEM_HU(0xDF8, (int64_t)(int32_t)0x80136000), (unsigned)MEM_HU(0xDFA, (int64_t)(int32_t)0x80136000)); }
    { /* PATCH: s6037 ddclamp */ static int on6037 = -1;
      if (on6037 < 0) { const char* e = getenv("ROGUESQ_DRAW_DISTANCE"); on6037 = (e && *e && atof(e) != 1.0 && !getenv("ROGUESQ_DD_NOCLAMP")) ? 1 : 0; }
      /* s6879 wideclamp: a widened footprint at dd 1 also passes 64 rows (21:9 lvl1 d=67): the span tables 0x80130DB0/0x80131DB0 overrun into this window (0x80808080) and the slot array into the descriptor, 4/4 crash.
         Same 64x64 bound, no area cap: retail runs past it (req 975 on cap 600). k = 1 stays retail. */
      extern double rs64_s6879_fpk; const int wide6879 = !on6037 && rs64_s6879_fpk != 1.0;
      if ((on6037 || wide6879) && MEM_W(4, (int64_t)(int32_t)0x80136DC0) != 0) {
        int64_t h = (int64_t)(int32_t)0x80132000, t = (int64_t)(int32_t)0x80136000;
        int32_t tw = (int32_t)MEM_HU(0xDF8, t), th = (int32_t)MEM_HU(0xDFA, t);
        int32_t x0 = (int32_t)MEM_W(0xDB0, h), x1 = (int32_t)MEM_W(0xDB4, h), z0 = (int32_t)MEM_W(0xDB8, h), z1 = (int32_t)MEM_W(0xDBC, h);
        /* s6053: at this point DB4/DBC are still EXCLUSIVE MAXIMA (ceil of polygon max); 0x80042A30 later does DB4-=DB0, DBC-=DB8 to make counts.
           s6040 clamped them as counts, so DB4=tw-x0 then lost x0 again at 2A30 -> negative u32-wrapped counts (s6052 w=4294967286). Clamp as maxima. */
        { int32_t cap = wide6879 ? 0 : (int32_t)MEM_HU(0xC4C, (int64_t)(int32_t)0x80130000);
          /* s6586b capx: host-side multiplier on the clamp cap only (guest 0xC4C untouched); ROGUESQ_DD_CAPX_TOG=N alternates 1x/capx every N calls */
          { static double cx = -1; static int ctg = -1; static unsigned cn = 0; static int clast = -1;
            if (cx < 0) { const char* e = getenv("ROGUESQ_DD_CAPX"); cx = (e && *e) ? atof(e) : 1.0; const char* t2 = getenv("ROGUESQ_DD_CAPX_TOG"); ctg = t2 ? atoi(t2) : 0; }
            double use = cx; if (ctg > 0) { int b = (int)((cn++ / (unsigned)ctg) & 1u); use = b ? cx : 1.0; if (b != clast) { clast = b; fprintf(stderr, "[capxtog] blk=%d capx=%g\n", b, use); } }
            if (use != 1.0 && cap > 0) cap = (int32_t)(cap * use); }
          /* s6548 log */ static int n6548 = 0; int cx_log6586 = getenv("ROGUESQ_DD_CAPX_TOG") && atoi(getenv("ROGUESQ_DD_CAPX_TOG")) != 0; /* s7734: same reading as ctg */ int32_t px0 = x0, px1 = x1, pz0 = z0, pz1 = z1;
          /* s6874 edge: retail's window legally runs past the map; getGridCellValueAt sends those cells to clampGridCellLookup (0x80048948), which repeats the edge cell, so the plain continues to the horizon.
             Clamping to tw/th deleted that border at any dd != 1 (lvl1 k2: map edge against the sky, tris 1026 -> 509). Keep it; spend the cap and slot64 limits on off-map cells first. ROGUESQ_DD_EDGE=0 = old. */
          static int edge6874 = -1; if (edge6874 < 0) { const char* e = getenv("ROGUESQ_DD_EDGE"); edge6874 = (e && *e == '0') ? 0 : 1; }
          if (!edge6874) { if (x0 < 0) x0 = 0; if (x1 > tw) x1 = tw; if (x1 < x0) x1 = x0;
            if (z0 < 0) z0 = 0; if (z1 > th) z1 = th; if (z1 < z0) z1 = z0; }
          else { while (cap > 0 && (x1 - x0) * (z1 - z0) > cap && z1 > th && (z1 - z0) > 1) z1--; while (cap > 0 && (x1 - x0) * (z1 - z0) > cap && z0 < 0 && (z1 - z0) > 1) z0++;
            while (cap > 0 && (x1 - x0) * (z1 - z0) > cap && x1 > tw && (x1 - x0) > 1) x1--; while (cap > 0 && (x1 - x0) * (z1 - z0) > cap && x0 < 0 && (x1 - x0) > 1) x0++;
            while (x1 - x0 > 64 && x1 > tw) x1--; while (x1 - x0 > 64 && x0 < 0) x0++; while (z1 - z0 > 64 && z1 > th) z1--; while (z1 - z0 > 64 && z0 < 0) z0++; }
          while (cap > 0 && (x1 - x0) * (z1 - z0) > cap && (z1 - z0) > 1) z1--; while (cap > 0 && (x1 - x0) * (z1 - z0) > cap && (x1 - x0) > 1) x1--;
          /* s6591 slot64: the per-cell slot array at 0x80132DC0 is 64 words wide x 64 rows (0x4000, ends exactly at the terrain descriptor 0x80136DC0); stores at 0x80043020 index it by (row<<8)+4*col, so a window with d>64 rows clears the descriptor (s6591 descwatch: val 0 to 80136DC0/C4). Cap the window at 64x64. */
          if (x1 - x0 > 64) x1 = x0 + 64; if (z1 - z0 > 64) z1 = z0 + 64;
          if (getenv("ROGUESQ_DD_LOG") && (n6548++ % (cx_log6586 ? 6 : 60)) == 0) fprintf(stderr, "[ddclamp] pre x[%d,%d) z[%d,%d) tw=%d th=%d cap=%d post x[%d,%d) z[%d,%d)\n", px0, px1, pz0, pz1, tw, th, cap, x0, x1, z0, z1); }
        MEM_W(0xDB0, h) = (uint32_t)x0; MEM_W(0xDB4, h) = (uint32_t)x1; MEM_W(0xDB8, h) = (uint32_t)z0; MEM_W(0xDBC, h) = (uint32_t)z1;
        ctx->r7 = (int64_t)x0; ctx->r6 = (int64_t)z0;
      } }
'''
def apply9(text):
    if "PATCH: s6037 ddclamp" in text and "s6586b capx" in text and "s6590 desc log" in text and "s6591 slot64" in text and "ROGUESQ_DD_NOCLAMP" in text and "s6874 edge" in text and "s6879 wideclamp" in text or OLD not in text: return text, 0
    if "PATCH: s6037 ddclamp" in text:
        i = text.index("    { /* s6590 desc log */") if "s6590 desc log" in text else text.index("    { /* PATCH: s6037 ddclamp */"); j = text.index(OLD, i); text = text[:i] + text[j:]
    assert text.count(OLD) == 1
    return text.replace(OLD, NEW + OLD), 1
if __name__ == "__main__":
    p = base / "funcs_9.c"; t = p.read_text(); t2, n = apply9(t)
    if n: p.write_text(t2)
    print("funcs_9.c live patched x%d" % n)
