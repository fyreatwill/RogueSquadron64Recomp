#!/usr/bin/env python3
"""s7126 wsheet-escape: summarise a ROGUESQ_W_KEEPLOG (kept perspective tris with W<=0 = class M, or min/max W < 1/64 = class P)
against the DROPLOG of the same run, and optionally list the long kept tris near given capture frames.
usage: s7126_keep.py keep.txt drop.txt [idx swap,swap,...] [--win ms] [--minspan px]
  idx: s7124_capidx.py output (swap mach ...); for each listed swap prints kept tris with span >= minspan in [mach-win, mach]."""
import sys, collections
keep, drop = sys.argv[1], sys.argv[2]
args = sys.argv[3:]; win = 60.0; minspan = 100.0
if '--win' in args: i = args.index('--win'); win = float(args[i+1]); del args[i:i+2]
if '--minspan' in args: i = args.index('--minspan'); minspan = float(args[i+1]); del args[i:i+2]
B = [20, 40, 60, 100, 150, 200, 400, 1e9]
def bk(s): return next(i for i, b in enumerate(B) if s < b)
cnt = collections.Counter(); rows = []
for ln in open(keep):
    p = ln.split()
    if len(p) != 12: continue
    t = int(p[0]); c = p[1]; v = list(map(float, p[2:]))
    cnt[(c, bk(v[9]))] += 1; rows.append((t, c, v))
nd = sum(1 for _ in open(drop))
print('kept tris by class/span bucket (upper bounds px):', B[:-1])
for c in 'MP': print(c, [cnt[(c, i)] for i in range(len(B))])
print('drops logged:', nd)
# ratio stats for long P tris
lp = [r for r in rows if r[1] == 'P' and r[2][9] >= minspan]
print('P span>=%g: %d; min W ratio quantiles:' % (minspan, len(lp)), end=' ')
rs = sorted(min(r[2][6:9]) / max(r[2][6:9]) for r in lp)
print([round(rs[int(q * (len(rs) - 1))], 5) for q in (0, .1, .5, .9, 1)] if rs else '-')
# episodes of long kept tris (gap > 50 ms splits)
eps = []; T = 24e6 / 1e3
for r in sorted([r for r in rows if r[2][9] >= minspan]):
    if eps and r[0] - eps[-1][-1][0] < 50 * T: eps[-1].append(r)
    else: eps.append([r])
print('episodes of kept tris span>=%g: %d' % (minspan, len(eps)))
for e in eps[:40]:
    cl = collections.Counter(r[1] for r in e); mx = max(e, key=lambda r: r[2][9])
    print('  t0=%d dur=%.0fms n=%d cls=%s maxspan=%.0f W=%s v=%s' % (e[0][0], (e[-1][0] - e[0][0]) / T, len(e), dict(cl), mx[2][9],
          ' '.join('%.4g' % w for w in mx[2][6:9]), ' '.join('%.0f' % x for x in mx[2][:6])))
if args:
    idx = {int(l.split()[0]): int(l.split()[1]) for l in open(args[0])}
    for s in map(int, args[1].split(',')):
        m = idx.get(s)
        if m is None: print('swap', s, 'not in idx'); continue
        near = [r for r in rows if m - win * T <= r[0] <= m and r[2][9] >= minspan]
        print('swap %d mach %d: %d kept tris span>=%g in %.0f ms before' % (s, m, len(near), minspan, win))
        for r in near[:12]:
            print('   %+.1fms %s span=%.0f v=%s W=%s' % ((r[0] - m) / T, r[1], r[2][9], ' '.join('%.0f' % x for x in r[2][:6]), ' '.join('%.4g' % w for w in r[2][6:9])))
