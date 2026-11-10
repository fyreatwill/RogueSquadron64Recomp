#!/usr/bin/env python3
"""s7101 H-order: does the terrain builder read the camera translation the chase wrote THIS tick, the previous tick's,
or a transient value? Input: ROGUESQ_S7101_CHASE log with ch (chase step, pre-step pos) and bv (builder read) lines.
Chase final pos of tick i = pre-step pos logged at tick i+1. Only bv reads of the flight camera (cam of the ch lines)
that sit between two consecutive ch lines are classed. Per lim: == final this tick / == pre-step (previous tick) / other,
plus |read - final| for the others. Then the s7100 episode windows (--res soak.log --csv drops.csv) are classed too.
usage: s7101_bvread.py chase.txt [drops.csv split_res.txt]"""
import re, sys, bisect, ast
from collections import Counter
ev = []
for l in open(sys.argv[1], errors='replace'):
    d = dict(re.findall(r'(\w+)=(\S+)', l))
    try:
        if l.startswith('ch ') and 'off' in d:
            ev.append(('c', int(d['m']), int(d['lim']), tuple(map(float, d['pos'].split(','))), d['cam']))
        elif l.startswith('bv ') and 'rd' in d:
            ev.append(('b', int(d['m']), int(d['fc']), tuple(map(float, d['rd'].split(','))), d['cam']))
    except ValueError:
        pass
rows = []  # (m, lim, class, dev)
for i in range(1, len(ev) - 1):
    e = ev[i]
    if e[0] != 'b': continue
    p, n = ev[i - 1], ev[i + 1]
    if p[0] != 'c' or n[0] != 'c' or e[4] != p[4]: continue
    fin, pre, r = n[3], p[3], e[3]
    df = max(abs(r[k] - fin[k]) for k in range(3)); dp = max(abs(r[k] - pre[k]) for k in range(3))
    cl = 'final' if df < 1e-4 else ('prev' if dp < 1e-4 else 'other')
    rows.append((e[1], p[2], cl, df))
for lim in (1, 2):
    R = [x for x in rows if x[1] == lim]
    if not R: continue
    c = Counter(x[2] for x in R)
    o = sorted(x[3] for x in R if x[2] == 'other')
    print('lim=%d reads %d final %d prev %d other %d other_dev_median %.4f max %.4f' % (lim, len(R), c['final'], c['prev'], c['other'],
          o[len(o) // 2] if o else 0, o[-1] if o else 0))
if len(sys.argv) >= 4:
    drows = [l.split(',') for l in open(sys.argv[2])][1:]
    cap0 = int(drows[0][6]) - float(drows[0][1]) * 24e6
    M = [x[0] for x in rows]
    for l in open(sys.argv[3], errors='replace'):
        g = re.match(r'lim=(\d+) span .* times (\[.*\])', l)
        if not g: continue
        ts = ast.literal_eval(g.group(2)); ep = [t for i, t in enumerate(ts) if i == 0 or t - ts[i - 1] > 1.0]
        for t in ep:
            m = cap0 + t * 24e6; i0 = bisect.bisect_left(M, m - 0.3 * 24e6); i1 = bisect.bisect_right(M, m + 0.1 * 24e6)
            c = Counter(x[2] for x in rows[i0:i1])
            print('EP lim=%s t=%.1f reads %d %s maxdev %.4f' % (g.group(1), t, i1 - i0, dict(c), max([x[3] for x in rows[i0:i1] if x[2] == 'other'] or [0])))
