#!/usr/bin/env python3
"""s6905 G5b: instrument and lever for the dd>1 window on maps no wider than the window. s6904 logged windows that keep off-map cells while dropping
on-map ones (lvl1 dd4 pre x[-100,47) z[-75,94), post x[-22,42) z[10,74); tw=th=64). Offline replay of logged bounds (scratch/s6905/sim.py) says a plain slide
toward the map costs near ground, so the slide here is near-guarded: it stops where a dd1-sized wedge (32 cells, +-52 deg) would leave the window.
ROGUESQ_DD_MAPWIN=1|tog (default 0, no change): in on blocks use K = ROGUESQ_DD_MAPWIN_K (default the FWDWIN K) and, with ROGUESQ_DD_MAPWIN_SLIDE=1, the slide.
tog = 6 s blocks, [mapwin] on=N in stderr. Trace: site 16 = on, x slid, z slid, on-map cells lost after placement.
Runs after apply_s6902_fwdtog in RS64_REPLAY.  Usage: apply_s6905_mapwin.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s6905 mapwin"
f = D / "funcs_9.c"
t = f.read_text(errors="surrogateescape")
if TAG in t: print("already applied"); sys.exit(0)
A = "                a = (int32_t)floorf(qx.f + k6901 * dx - 0.5f * (float)w); if (a > px1 - w) a = px1 - w; if (a < px0) a = px0; x0 = a; x1 = a + w;\n"
B = "                a = (int32_t)floorf(qz.f + k6901 * dz - 0.5f * (float)d); if (a > pz1 - d) a = pz1 - d; if (a < pz0) a = pz0; z0 = a; z1 = a + d;\n"
H = r'''                /* PATCH: s6905 mapwin */ static int m6905 = -1, sl6905 = 0, last6905 = -1; static float km6905 = -1.0f; int on6905 = 0; float kk6905 = k6901;
                if (m6905 < 0) { const char* e = getenv("ROGUESQ_DD_MAPWIN"); m6905 = !(e && *e) ? 0 : (e[0] == 't' ? 2 : (e[0] != '0')); e = getenv("ROGUESQ_DD_MAPWIN_K"); if (e && *e) km6905 = (float)atof(e); e = getenv("ROGUESQ_DD_MAPWIN_SLIDE"); sl6905 = e && *e == '1'; }
                if (m6905 == 2) { on6905 = (int)((mach_absolute_time() / (uint64_t)144000000u) & 1u); if (on6905 != last6905) { last6905 = on6905; fprintf(stderr, "[mapwin] on=%d\n", on6905); } } else on6905 = m6905;
                if (on6905 && km6905 >= 0.0f) kk6905 = km6905;
'''
S = r'''                { int32_t sx6905 = 0, sz6905 = 0; /* PATCH: s6905 slide */
                  const int32_t lx = x0 > 0 ? (x0 < tw ? x0 : tw) - (px0 > 0 ? px0 : 0) : 0, hx = (px1 < tw ? px1 : tw) - (x1 > 0 ? x1 : 0), lz = z0 > 0 ? (z0 < th ? z0 : th) - (pz0 > 0 ? pz0 : 0) : 0, hz = (pz1 < th ? pz1 : th) - (z1 > 0 ? z1 : 0);
                  if (on6905 && sl6905) { const float c = 0.616f, s = 0.788f, ax1 = dx * c - dz * s, ax2 = dx * c + dz * s, az1 = dx * s + dz * c, az2 = -dx * s + dz * c, R = 32.0f;
                    float nl = fminf(0.0f, fminf(ax1, ax2)), nh = fmaxf(0.0f, fmaxf(ax1, ax2)), ml = fminf(0.0f, fminf(az1, az2)), mh = fmaxf(0.0f, fmaxf(az1, az2));
                    if (dx < -c) nl = -1.0f; if (dx > c) nh = 1.0f; if (dz < -c) ml = -1.0f; if (dz > c) mh = 1.0f;
                    const int32_t gxl = (int32_t)floorf(qx.f + R * nl), gxh = (int32_t)ceilf(qx.f + R * nh), gzl = (int32_t)floorf(qz.f + R * ml), gzh = (int32_t)ceilf(qz.f + R * mh);
                    int32_t up = x0 < 0 ? -x0 : 0, dn = x1 > tw ? x1 - tw : 0; if (up > hx) up = hx; if (dn > lx) dn = lx; if (up > gxl - x0) up = gxl - x0; if (dn > x1 - gxh) dn = x1 - gxh; if (up < 0) up = 0; if (dn < 0) dn = 0;
                    sx6905 = up - dn; x0 += sx6905; x1 += sx6905;
                    up = z0 < 0 ? -z0 : 0; dn = z1 > th ? z1 - th : 0; if (up > hz) up = hz; if (dn > lz) dn = lz; if (up > gzl - z0) up = gzl - z0; if (dn > z1 - gzh) dn = z1 - gzh; if (up < 0) up = 0; if (dn < 0) dn = 0;
                    sz6905 = up - dn; z0 += sz6905; z1 += sz6905; }
                  if (rs64_g3e_on()) rs64_g3e_trace(16, (uint32_t)on6905, (uint32_t)sx6905, (uint32_t)sz6905, (uint32_t)((lx > 0 ? lx : 0) + (hx > 0 ? hx : 0) + (lz > 0 ? lz : 0) + (hz > 0 ? hz : 0))); }
'''
assert t.count(A) == 1 and t.count(B) == 1, (t.count(A), t.count(B))
t = t.replace(A, H + A.replace("k6901", "kk6905"), 1).replace(B, B.replace("k6901", "kk6905") + S, 1)
f.write_text(t, errors="surrogateescape"); print("applied", TAG)
