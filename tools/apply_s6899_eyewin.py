#!/usr/bin/env python3
"""s6899 G5b: dd>1 lost the ground near the eye. ORIGIN: our own s6037/s6874/s6591 window clamp in binPolygonIntoTerrainGrid. A footprint
wider than 64 cells is trimmed with no regard to the eye: off-map cells first, then the high end, so it stays anchored low. LEVEL=4 cutscene,
eye cell 78,79 (polygon point 0 = cam/2, measured): dd1 window x[51,101) z[79,103), dd4 window [0,64) on both axes, near quads 8 vs 278 per swap.
Fix: after all trims, slide the window minimally (width unchanged, inside the pre-clamp bounds) so it holds eye +-26 cells, about what dd1
draws. A slide of only +-2 left a hard water edge (scratch/s6899/sheet_scene.png). ROGUESQ_DD_EYEWIN=0 old, =tog odd mach seconds.
Trace: site 11 = p0x, p0z float bits, x0, z0; 12 = slid (x0 before, after, z0 before, after); 13 = pre-clamp x0 x1 z0 z1; 14 = tw th.
Usage: apply_s6899_eyewin.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6899 eyewin"
f = D / "funcs_9.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = "          if (x1 - x0 > 64) x1 = x0 + 64; if (z1 - z0 > 64) z1 = z0 + 64;\n"
N = A + r'''          { /* PATCH: s6899 eyewin */ static int on6899 = -1; extern uint64_t mach_absolute_time(void);
            if (on6899 < 0) { const char* e = getenv("ROGUESQ_DD_EYEWIN"); on6899 = !(e && *e) ? 1 : (e[0] == 't' ? 2 : (e[0] != '0')); }
            union { uint32_t u; float f; } qx, qz; qx.u = (uint32_t)MEM_W(0, ctx->r4); qz.u = (uint32_t)MEM_W(8, ctx->r4);
            const int32_t ex = (int32_t)floorf(qx.f), ez = (int32_t)floorf(qz.f), ax = x0, az = z0;
            if (rs64_g3e_on()) rs64_g3e_trace(11, qx.u, qz.u, (uint32_t)x0, (uint32_t)z0);
            if (rs64_g3e_on()) { rs64_g3e_trace(13, (uint32_t)px0, (uint32_t)px1, (uint32_t)pz0, (uint32_t)pz1); rs64_g3e_trace(14, (uint32_t)tw, (uint32_t)th, 0, 0); }
            if (on6899 == 1 || (on6899 == 2 && ((mach_absolute_time() / 24000000u) & 1u))) {
              /* keep what dd1 draws: eye +-R cells, minimal slide, bounded by the pre-clamp window; width unchanged */
              const int32_t sx = x1 - x0, sz = z1 - z0, rx = sx / 2 - 1 < 26 ? sx / 2 - 1 : 26, rz = sz / 2 - 1 < 26 ? sz / 2 - 1 : 26; int32_t lo, hi;
              hi = ex + rx + 1 < px1 ? ex + rx + 1 : px1; lo = ex - rx > px0 ? ex - rx : px0;
              if (hi > x1) { x1 = hi; x0 = x1 - sx; } else if (lo < x0) { x0 = lo; x1 = x0 + sx; }
              hi = ez + rz + 1 < pz1 ? ez + rz + 1 : pz1; lo = ez - rz > pz0 ? ez - rz : pz0;
              if (hi > z1) { z1 = hi; z0 = z1 - sz; } else if (lo < z0) { z0 = lo; z1 = z0 + sz; }
              if ((ax != x0 || az != z0) && rs64_g3e_on()) rs64_g3e_trace(12, (uint32_t)ax, (uint32_t)x0, (uint32_t)az, (uint32_t)z0); } }
'''
assert t.count(A) == 1, t.count(A)
f.write_text(t.replace(A, N, 1), errors="surrogateescape"); print("applied", TAG)
