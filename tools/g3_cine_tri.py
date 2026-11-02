#!/usr/bin/env python3
"""s6795 G3 cinematic TRI-flag check: is a per-shot tri-median gap (g3_cine_sweep TRI flag) different content or frame weighting?

  g3_cine_tri.py RETAIL.tsv PORT.tsv RLOG RSTART:RLEN PSTART:PLEN RT0 SHOT [SHOT...]
      e.g. scratch/s6792/mr.tsv scratch/s6792/vp.tsv scratch/s6792/mov/retail/oracle.log 500:19858 12595:22039 200 48 64
  Per shot: tri quantiles, DTW content cost (mean |dtri| / mean tri on the best monotonic frame alignment) with a
  cross-shot CONTROL (same retail shot vs the neighbouring port shots) and a POSITIVE CONTROL (port tris x1.3 on every
  2nd frame = H-dup-like, and on all frames = H-lod-like), the retail-frame-weighted port median along the DTW path,
  and the low-tri prefix (frames/seconds before the shot first crosses its mid tri count) in each.
  Same content: DTW cost << control and << positive control; then a median gap is frame weighting (H-timing), not tris.
"""
import sys, os, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g3_cine_sweep as g

def dtw(a, b):
    n, m = len(a), len(b); INF = float('inf'); D = [[INF] * (m + 1) for _ in range(n + 1)]; D[0][0] = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = abs(a[i - 1] - b[j - 1]) + min(D[i - 1][j], D[i][j - 1], D[i - 1][j - 1])
    i, j, path = n, m, []
    while i > 0 and j > 0:
        path.append((i - 1, j - 1)); c = min((D[i - 1][j - 1], 0), (D[i - 1][j], 1), (D[i][j - 1], 2))[1]
        i, j = (i - 1, j - 1) if c == 0 else (i - 1, j) if c == 1 else (i, j - 1)
    return path[::-1]

def cost(a, b):
    p = dtw(a, b); m = {}
    for i, j in p: m.setdefault(i, []).append(b[j])
    return st.mean(abs(a[i] - b[j]) for i, j in p) / st.mean(a), st.median(st.mean(m[i]) for i in range(len(a)))

if __name__ == '__main__':
    rp, pp, rlog, rb, pb, t0 = sys.argv[1:7]; sel = lambda v: tuple(map(int, v.split(':')))
    R = g.block(rp, 640, sel(rb)); P = g.block(pp, 640, sel(pb)); RS = g.shots(R); PS = g.shots(P)
    sw = g.retail_swaps(rlog, 640, float(t0)); pt = [f[3] / 60.0 for f in P]
    q = lambda v: [sorted(v)[min(len(v) - 1, int(len(v) * x))] for x in (0, .1, .5, .9, 1)]
    for k in map(int, sys.argv[7:]):
        a = [f[0] for f in R[slice(*RS[k])]]; b = [f[0] for f in P[slice(*PS[k])]]
        c, pm = cost(a, b)
        ctl = min(cost(a, [f[0] for f in P[slice(*PS[j])]])[0] for j in (k - 1, k + 1) if 0 <= j < len(PS))
        pa = cost(a, [int(t * 1.3) if i % 2 else t for i, t in enumerate(b)])[0]; pl = cost(a, [int(t * 1.3) for t in b])[0]
        mid = (min(a) + max(a)) / 2; ri = next(i for i, t in enumerate(a) if t > mid); pi = next(i for i, t in enumerate(b) if t > mid)
        rs = sw[RS[k][0]:RS[k][1] + 1]; ps = pt[PS[k][0]:PS[k][1]]
        print('shot %d: frames r %d p %d; quantiles(0/.1/.5/.9/1) r %s p %s' % (k, len(a), len(b), q(a), q(b)))
        print('   DTW cost %.3f | cross-shot ctl %.3f | pos ctl x1.3 alt %.3f all %.3f | median r %d, port-on-retail-frames %d'
              % (c, ctl, pa, pl, st.median(a), pm))
        print('   low-tri prefix: r %d frames / %.1f s, p %d frames / %.1f s; frames after prefix r %d p %d'
              % (ri, rs[ri] - rs[0], pi, ps[pi] - ps[0], len(a) - ri, len(b) - pi))
