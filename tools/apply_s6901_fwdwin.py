#!/usr/bin/env python3
"""s6901 G5b: at dd>1 the far terrain dropped by half with camera heading, in flight. ORIGIN: our own s6037/s6874/s6591 window clamp in
binPolygonIntoTerrainGrid again, two faults. (1) Order: the area-cap loops trim z while x is still its pre-clamp width (~210), so z is
over-trimmed before x ever reaches 64: LEVEL=4 dd4 headings 240-300 window 64x40. (2) Anchor: past 64 the high end is trimmed, so the window
stays anchored low, and a heading whose side ray swings behind the eye on an axis pulls the window back off the forward side: passing a
diagonal, quads 3500 -> 1790 and forward reach 63 -> 37 cells within 0.2 s, then back. dd1 never enters this path; reach is heading-flat.
Fix: place the window from the pre-clamp bounds. Forward = bounds centre minus eye (dot with the true camera forward 0.99+, s6901 sim.py).
Per axis: width min(bounds, 64); centre = eye + K * forward (K = 26 cells, ROGUESQ_DD_FWDWIN_K); kept inside the bounds. It moves continuously
with heading. The area cap is still honoured, spent on the axis that faces the view least. Replaces the s6899 slide when armed: the sim holds
a dd1-sized frustum at cover 1.00 on every heading. dd>1 only; ROGUESQ_DD_FWDWIN=0 old, =tog odd mach seconds.
Trace: site 15 = x0 x1 z0 z1 of the placed window.
Runs after apply_s6899_eyewin in RS64_REPLAY.  Usage: apply_s6901_fwdwin.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6901 fwdwin"
f = D / "funcs_9.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = "            if (on6899 == 1 || (on6899 == 2 && ((mach_absolute_time() / 24000000u) & 1u))) {\n"
N = r'''            /* PATCH: s6901 fwdwin */ static int on6901 = -1; static float k6901 = 26.0f; int fw6901 = 0;
            if (on6901 < 0) { const char* e = getenv("ROGUESQ_DD_FWDWIN"); on6901 = !(e && *e) ? 1 : (e[0] == 't' ? 2 : (e[0] != '0')); e = getenv("ROGUESQ_DD_FWDWIN_K"); if (e && *e) k6901 = (float)atof(e); }
            if (on6037 && edge6874 && px1 > px0 && pz1 > pz0 && (on6901 == 1 || (on6901 == 2 && ((mach_absolute_time() / 24000000u) & 1u)))) {
              float dx = 0.5f * (float)(px0 + px1) - qx.f, dz = 0.5f * (float)(pz0 + pz1) - qz.f; const float n = sqrtf(dx * dx + dz * dz);
              if (n > 0.001f) { int32_t w = px1 - px0 < 64 ? px1 - px0 : 64, d = pz1 - pz0 < 64 ? pz1 - pz0 : 64, a; dx /= n; dz /= n; fw6901 = 1;
                while (cap > 0 && w * d > cap && (w > 1 || d > 1)) { if ((fabsf(dx) >= fabsf(dz) && d > 1) || w <= 1) d--; else w--; }
                a = (int32_t)floorf(qx.f + k6901 * dx - 0.5f * (float)w); if (a > px1 - w) a = px1 - w; if (a < px0) a = px0; x0 = a; x1 = a + w;
                a = (int32_t)floorf(qz.f + k6901 * dz - 0.5f * (float)d); if (a > pz1 - d) a = pz1 - d; if (a < pz0) a = pz0; z0 = a; z1 = a + d;
                if (rs64_g3e_on()) rs64_g3e_trace(15, (uint32_t)x0, (uint32_t)x1, (uint32_t)z0, (uint32_t)z1); } }
            if (!fw6901 && (on6899 == 1 || (on6899 == 2 && ((mach_absolute_time() / 24000000u) & 1u)))) {
'''
assert t.count(A) == 1, t.count(A)
f.write_text(t.replace(A, N, 1), errors="surrogateescape"); print("applied", TAG)
