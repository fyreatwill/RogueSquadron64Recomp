#!/usr/bin/env python3
"""s6791 G3f: summarise a ROGUESQ_G3F_CAM log. Columns: t n cam w h fovy aspect near far scale m[12] (cam+0x2C).
usage: g3f_cam_scan.py cam.txt [--cam PTR] [--t0 S --t1 S] [--rows]
Prints per camera: calls, t range, fovy/aspect/near/far/scale min/max, and the 3x3 rotation's worst row-norm and
row-dot deviation (a lerped, unnormalised camera matrix shows up as norm != 1 / dot != 0). --rows prints every call
in the window with yaw (atan2 of row 0) and per-call yaw step."""
import sys, math, argparse
ap = argparse.ArgumentParser(); ap.add_argument('f'); ap.add_argument('--cam'); ap.add_argument('--t0', type=float, default=-1e9)
ap.add_argument('--t1', type=float, default=1e9); ap.add_argument('--rows', action='store_true'); a = ap.parse_args()
cams = {}
for ln in open(a.f):
    p = ln.split()
    if len(p) < 22: continue
    t = float(p[0])
    if not (a.t0 <= t <= a.t1) or (a.cam and p[2] != a.cam): continue
    v = [float(x) for x in p[5:22]]
    cams.setdefault(p[2], []).append((t, int(p[1]), int(p[3]), int(p[4]), v))
for c, rs in cams.items():
    def rng(i): xs = [r[4][i] for r in rs]; return '%.5g..%.5g' % (min(xs), max(xs))
    nd = dd = 0.0
    for r in rs:
        m = r[4][5:14]; R = [m[0:3], m[3:6], m[6:9]]
        for i in range(3):
            nd = max(nd, abs(math.sqrt(sum(x * x for x in R[i])) - 1))
            for j in range(i + 1, 3): dd = max(dd, abs(sum(R[i][k] * R[j][k] for k in range(3))))
    print('cam %s calls %d t %.2f..%.2f wh %s fovy %s aspect %s near %s far %s scale %s | max|rownorm-1| %.4g max|rowdot| %.4g'
          % (c, len(rs), rs[0][0], rs[-1][0], sorted({(r[2], r[3]) for r in rs}), rng(0), rng(1), rng(2), rng(3), rng(4), nd, dd))
    if a.rows:
        py = None
        for r in rs:
            m = r[4][5:14]; yaw = math.degrees(math.atan2(m[2], m[0]))
            n0 = math.sqrt(sum(x * x for x in m[0:3])); n2 = math.sqrt(sum(x * x for x in m[6:9]))
            print('  t %.4f n %d fovy %.4g asp %.4g yaw %8.3f dyaw %7.3f n0 %.4f n2 %.4f pos %s' % (r[0], r[1], r[4][0], r[4][1], yaw,
                  0 if py is None else yaw - py, n0, n2, ' '.join('%.1f' % x for x in r[4][14:17])))
            py = yaw
