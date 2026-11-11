#!/usr/bin/env python3
"""s7107 fps60-wall-painter: whole-run stream-level loss detector on a ROGUESQ_G5B_TRIS + ROGUESQ_S7107_TAG stream.
Per swap i: lost = grid cells painted last by a TRI_GEN tri (tag < 0x80) on swap i-2 and not on swap i (tools/s7107_painter.py grid).
For every swap with lost >= MIN: the reference painter tags over the lost cells (7x7 cell labels relative to the eye), the minimum
z (top 16 bits) of the near (ring <= 1) cells' tris in the reference and dropped swap, the near cells' tri counts, and whether the
capture (g5b_drops csv rows, any T) flags a frame within 100 ms (independent line: the presented window).
usage: s7107_losscan.py tris.bin drops.csv [MIN=300] [G=16]"""
import sys, struct, bisect
sys.argv += [] ; tb, dcsv = sys.argv[1:3]; MIN = int(sys.argv[3]) if len(sys.argv) > 3 else 300
G = int(sys.argv[4]) if len(sys.argv) > 4 else 16
sys.argv = [sys.argv[0], tb, dcsv, '/dev/null', str(G)]
src = open(__file__.replace('s7107_losscan', 's7107_painter')).read().split('mach = [s[1] for s in SW]')[0]
src = src.replace("print('control FIFO", "0 and print('control FIFO")
exec(src)
from collections import Counter
rows = [l.strip().split(',') for l in open(dcsv)][1:]
ev = sorted((int(r[6]), float(r[4]), float(r[1])) for r in rows); em = [e[0] for e in ev]
cap0 = ev[0][0] - ev[0][2] * 24e6
NEAR = {(dz + 3) * 7 + dx + 3 for dz in (-1, 0, 1) for dx in (-1, 0, 1)}
cache = {}
def gi(i):
    if i not in cache:
        cache[i] = grid(i)
        if i - 3 in cache: del cache[i - 3]
    return cache[i]
def nearinfo(inf):
    n = sum(v[0] for k, v in inf.items() if k in NEAR); z = min((v[5] for k, v in inf.items() if k in NEAR), default=0xFFFFFFFF)
    return n, z >> 16
hits = []; hist = Counter()
for i in range(2, len(SW)):
    ga, ia = gi(i - 2); gb, ib = gi(i); L = lost(ga, gb); hist[min(len(L) // 100, 9)] += 1
    if len(L) < MIN: continue
    t = SW[i][1]; j = bisect.bisect_left(em, t - 0.1 * 24e6); cv = [ev[k] for k in range(j, len(ev)) if ev[k][0] <= t + 0.1 * 24e6]
    ra = Counter(lab(ga[c]) for c in L).most_common(3); rb = Counter(lab(gb.get(c)) for c in L).most_common(2)
    hits.append((i, len(L), ra, rb, nearinfo(ia), nearinfo(ib), cv))
print('lost-cell histogram (x100):', sorted(hist.items()))
print('swaps with lost >= %d: %d' % (MIN, len(hits)))
for i, n, ra, rb, na, nb, cv in hits:
    print('sw %5d t=%7.2f lost %4d ref %s -> %s  near tris/minz ref %d/%04X drop %d/%04X  cap %s' % (SW[i][0], (SW[i][1] - cap0) / 24e6, n, ra, rb,
          na[0], na[1], nb[0], nb[1], ['%.2f:%.2f' % (c[2], c[1]) for c in cv]))
