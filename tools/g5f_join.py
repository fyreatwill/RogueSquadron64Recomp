#!/usr/bin/env python3
"""s6906 G5f: join g5f_lines presented lines to g5f_thin triangles. A line in capture pixels maps to image pixels with
x = X/cw_cap*cw, y = (Y/caph*winh - bar)/(winh-bar)*H. A triangle matches when it sits in a swap stamped within the
window before the frame and its midpoint is within tol px of the line and its angle within 6 degrees.
usage: g5f_join.py <lines.txt> <thin.txt> [cw=796] [H=240] [cap_w=960] [cap_h=540] [winh=796] [bar=28] [tol=10]"""
import sys, bisect, math, collections
a = sys.argv; ln, tn = a[1], a[2]
cw, H, cpw, cph, winh, bar, tol = [float(x) for x in (a[3:10] + ['796', '240', '960', '540', '796', '28', '10'][len(a)-3:])]
thin = []
for l in open(tn):
    p = l.split(); thin.append((int(p[1]), int(p[0]), p[2], p[4], float(p[6]), float(p[7]), float(p[8]), float(p[9]), float(p[10]), int(p[11]), int(p[12])))
thin.sort(); T = [x[0] for x in thin]
tick = 24000000/1e9*1e9/24000000  # mach is 24 MHz here
W0, W1 = int(0.200*24e6), int(0.005*24e6)
c = collections.Counter(); rows = []
for l in open(ln):
    p = l.split(); idx, m = int(p[0]), int(p[1]); x0, y0, x1, y1 = [float(v) for v in p[2:6]]; run = int(p[6]); blk, inj = int(p[11]), int(p[12])
    if inj: continue
    mp = lambda X, Y: (X/cpw*cw, (Y/cph*winh-bar)/(winh-bar)*H)
    (u0, v0), (u1, v1) = mp(x0, y0), mp(x1, y1)
    ang = math.degrees(math.atan2(v1-v0, u1-u0)) % 180; dn = math.hypot(u1-u0, v1-v0) or 1
    best = None
    for i in range(bisect.bisect_left(T, m-W0), bisect.bisect_right(T, m+W1)):
        t = thin[i]; da = abs(ang-t[6]); da = min(da, 180-da)
        d = abs((t[7]-u0)*(v1-v0)-(t[8]-v0)*(u1-u0))/dn
        if da < 6 and d < tol and (best is None or d < best[0]): best = (d, t)
    k = 'join' if best else 'nojoin'
    if best: k += '_tr' if best[1][9] else '_per'
    c[(blk, k)] += 1; rows.append((idx, m, blk, run, ang, k, best[1][2:4] if best else None, best[1][4:6] if best else None))
for k in sorted(c): print('block', k[0], k[1], c[k])
print('sample'); [print(r) for r in rows[:: max(1, len(rows)//25)]]
