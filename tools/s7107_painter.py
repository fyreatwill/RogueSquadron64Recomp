#!/usr/bin/env python3
"""s7107 fps60-wall-painter: which terrain cell paints the near wall, and is it in the stream on the dropped frame?
Inputs: tris.bin (ROGUESQ_G5B_TRIS with ROGUESQ_S7107_TAG=1: pad byte = source tag, see src/rsp/s7106_rsptri.cpp), the g5b_drops
csv of the same run's capture, and the s7106 rt file (FIFO controls: q=depth,empty,push,pop,over).
Per swap: a last-painter grid (G px cells, even-odd test on the 5 edge vertices, draw order) labelled by tag class:
  T = TRI_GEN tri (tag < 0x80: 7x7 cell 0..48 or unmatched 0x40|cls), O = other command's tri.
Event: each g5b_drops row with T >= 0.12 (episode = rows within 1 s). Candidate swaps start in [ev - 0.30 s, ev + 0.05 s]; the
dropped swap is the one with the largest loss of T-painted cells vs the swap 2 earlier (the 'reference'). Lost mask = cells T in
the reference and not T in the dropped swap. Reported: reference painter tags over the mask, dropped-swap painters over the mask,
and for each top reference tag its tri count / bbox / z range in both swaps.
Control: the same lost-mask size for 200 random flight swap pairs 2 apart (the event must be an outlier); FIFO empty pops/overflows.
usage: s7107_painter.py tris.bin drops.csv rt.txt [G=16]"""
import sys, struct, mmap, re, random
from collections import Counter
tb, dcsv, rtf = sys.argv[1:4]; G = int(sys.argv[4]) if len(sys.argv) > 4 else 16
F = open(tb, 'rb'); d = mmap.mmap(F.fileno(), 0, access=mmap.ACCESS_READ)
M = b'\xf5\xf5\xf5\xf5'; SW = []  # (swap, mach, a, b)
p = d.find(M)
while p >= 0:
    n = d.find(M, p + 16)
    while n > 0 and (n - p - 16) % 32: n = d.find(M, n + 1)  # marker bytes inside a record: realign on the 32-byte grid
    t, q = struct.unpack_from('<QI', d, p + 4); SW.append((q, t, p + 16, n if n > 0 else len(d))); p = n
print('swaps in tris.bin %d' % len(SW))
# FIFO controls
emp = over = 0; dep = Counter(); kq = Counter(); nrt = 0
for l in open(rtf, errors='replace'):
    g = re.search(r' q=(\d+),(\d+),(\d+),(\d+),(\d+) kq=(\d+)', l)
    if not g: continue
    nrt += 1; emp += int(g.group(2)); over = max(over, int(g.group(5))); dep[min(int(g.group(1)), 99)] += 1; kq[int(g.group(6))] += 1
print('control FIFO: rt lines %d, empty pops %d, overflows %d, depth at swap %s, keys published %s' % (nrt, emp, over, dep.most_common(4), kq.most_common(3)))
def tris(i):
    q, t, a, b = SW[i]
    for k in range((b - a) // 32):
        op, tg, cw, tm, z = struct.unpack_from('<BBHII', d, a + k * 32); c = struct.unpack_from('<10h', d, a + k * 32 + 12)
        yield op, tg, cw, z, [(c[2 * j] / 4, c[2 * j + 1] / 4) for j in range(5)]
GW, GH = 1024 // G, 768 // G
def grid(i):
    g = {}; info = {}
    for op, tg, cw, z, P in tris(i):
        xs = [v[0] for v in P]; ys = [v[1] for v in P]
        e = info.setdefault(tg, [0, 1e9, 1e9, -1e9, -1e9, 0xFFFFFFFF, 0])
        e[0] += 1; e[1] = min(e[1], min(xs)); e[2] = min(e[2], min(ys)); e[3] = max(e[3], max(xs)); e[4] = max(e[4], max(ys))
        if op & 1: e[5] = min(e[5], z); e[6] = max(e[6], z)
        for gy in range(max(0, int(min(ys) // G)), min(GH, int(max(ys) // G) + 1)):
            y = gy * G + G / 2
            for gx in range(max(0, int(min(xs) // G)), min(GW, int(max(xs) // G) + 1)):
                x = gx * G + G / 2; ins = False
                for j in range(5):
                    x0, y0 = P[j]; x1, y1 = P[(j + 1) % 5]
                    if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0): ins = not ins
                if ins: g[(gx, gy)] = tg
    return g, info
isT = lambda t: t is not None and t < 0x80
def lost(ga, gb): return [c for c, t in ga.items() if isT(t) and not isT(gb.get(c))]
def lab(t):
    if t is None: return 'none'
    if t < 49: return 'c%+d%+d' % (t % 7 - 3, t // 7 - 3)
    if t < 0x80: return 'tgU%d' % (t & 0x3F)
    return 'op%02X' % (t & 0x7F) if t != 0xFF else 'untag'
mach = [s[1] for s in SW]
import bisect
rows = [l.strip().split(',') for l in open(dcsv)][1:]
evs = [(float(r[1]), int(r[6]), float(r[4])) for r in rows if float(r[4]) >= 0.12 and float(r[1]) >= 5]
eps = []
for e in evs:
    if not eps or e[0] - eps[-1][-1][0] > 1.0: eps.append([e])
    else: eps[-1].append(e)
print('events %d in %d episodes' % (len(evs), len(eps)))
# whole-run tag census on a sample of flight swaps + painter under the craft (positive control: near cells)
random.seed(7); flight = [i for i in range(2, len(SW)) if all(abs(SW[i][1] - e[1]) > 2 * 24e6 for e in evs)]
samp = random.sample(flight, min(200, len(flight))); base = []; under = Counter(); tagc = Counter()
for i in samp:
    ga, _ = grid(i - 2); gb, info = grid(i); base.append(len(lost(ga, gb)))
    for t, e in info.items(): tagc[lab(t) if t >= 49 else ('c' if t < 49 else '')] += e[0]
    xs = [c[0] for c in gb]; cx = (min(xs) + max(xs)) // 2 if xs else 0; ys = [c[1] for c in gb]; my = max(ys) if ys else 0
    under[lab(gb.get((cx, my - 2)))] += 1
base.sort()
print('control random flight pairs: lost cells median %d p90 %d p99 %d max %d' % (base[len(base) // 2], base[int(.9 * len(base))], base[int(.99 * len(base))], base[-1]))
print('control painter at bottom-centre (2 cells above the lowest painted row), flight sample:', under.most_common(6))
print('tri tag census (flight sample):', tagc.most_common(12))
for ep in eps:
    e = max(ep, key=lambda r: r[2]); lo = bisect.bisect_left(mach, e[1] - 0.30 * 24e6); hi = bisect.bisect_right(mach, e[1] + 0.05 * 24e6)
    cand = []
    gs = {}
    for i in range(max(2, lo), min(len(SW), hi)):
        for k in (i - 2, i):
            if k not in gs: gs[k] = grid(k)
        cand.append((len(lost(gs[i - 2][0], gs[i][0])), i))
    if not cand: print('episode t=%.1f: no swaps' % e[0]); continue
    print('\nepisode t=%.1f (T=%.2f, %d events) swaps %d..%d lost-cells per swap: %s' % (e[0], e[2], len(ep), lo, hi,
          ' '.join('%+.3f:%d' % ((SW[i][1] - e[1]) / 24e6, n) for n, i in cand)))
    n, i = max(cand); ga, ia = gs[i - 2]; gb, ib = gs[i]; L = lost(ga, gb)
    if n == 0: continue
    ra = Counter(lab(ga[c]) for c in L); rb = Counter(lab(gb.get(c)) for c in L)
    bb = [min(c[0] for c in L) * G, min(c[1] for c in L) * G, (max(c[0] for c in L) + 1) * G, (max(c[1] for c in L) + 1) * G]
    print('  dropped swap %d (dt %+.3f s): lost %d cells, region px %s; reference swap %d painters %s' % (SW[i][0], (SW[i][1] - e[1]) / 24e6, n, bb, SW[i - 2][0], ra.most_common(5)))
    print('  dropped-swap painters over the lost cells: %s' % rb.most_common(5))
    tt = Counter(ga[c] for c in L)
    for t, _ in tt.most_common(3):
        a = ia.get(t); b = ib.get(t); f = lambda e: 'n=%d bb=%.0f,%.0f..%.0f,%.0f z=%08X..%08X' % (e[0], e[1], e[2], e[3], e[4], e[5], e[6]) if e else 'ABSENT'
        print('   %-8s ref %s | drop %s' % (lab(t), f(a), f(b)))
    tot = lambda inf: (sum(v[0] for k, v in inf.items() if k < 49), sum(v[0] for k, v in inf.items() if 49 <= k < 0x80), sum(v[0] for k, v in inf.items() if k >= 0x80))
    print('  tris (7x7 cells, other TRI_GEN, non-TRI_GEN): ref %s drop %s' % (tot(ia), tot(ib)))
