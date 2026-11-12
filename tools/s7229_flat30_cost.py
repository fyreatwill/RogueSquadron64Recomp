#!/usr/bin/env python3
"""s7229: flat-30 census joined with per-second gfx-task cost, from a run log carrying ROGUESQ_G1B=1 [g1b] lines.
usage: s7229_flat30_cost.py LOG [LOG...]   [g1b] t=<s> vi=<VIs> tasks=<gfx tasks = game frames> sd_wall=<avg>/<max ms> sd_cpu=...
A flat run = >=8 consecutive seconds with tasks in 27..33 (2 VIs/frame), counted only after the first second with tasks>=45
(flight at FPS60). Prints per arm: seconds at >=55, 27..33, other; each flat run (start, length, mean sd_wall); mean sd_wall
in flat seconds vs 55+ seconds; mean load1. H-cost = sd_wall mean in flat runs > ~14 ms (frame cannot fit a 16.7 ms VI);
H-mode = flat runs with sd_wall well under budget."""
import sys, re
R = re.compile(r'^\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+) sd_wall=([0-9.]+)/(\d+) sd_cpu=([0-9.]+)/(\d+).*?load1=([0-9.]+)')
for path in sys.argv[1:]:
    rows = []
    for ln in open(path, errors='replace'):
        m = R.match(ln)
        if m: rows.append(tuple(float(x) for x in m.groups()))
    if not rows: print(path, 'NO g1b rows'); continue
    first = next((i for i, r in enumerate(rows) if r[2] >= 45), None)
    if first is None: print(path, 'never >=45 tasks/s', len(rows), 'rows'); continue
    fl = rows[first:]
    hi = [r for r in fl if r[2] >= 55]; fz = [r for r in fl if 27 <= r[2] <= 33]
    runs, cur = [], []
    for r in fl:
        if 27 <= r[2] <= 33: cur.append(r)
        else:
            if len(cur) >= 8: runs.append(cur)
            cur = []
    if len(cur) >= 8: runs.append(cur)
    mean = lambda v: sum(v) / len(v) if v else float('nan')
    print('%s: t=%d..%d  n=%d  >=55:%d  27-33:%d  other:%d  sd_wall mean >=55 %.2f ms | 27-33 %.2f ms  sd_cpu 27-33 %.2f  load1 %.2f' % (
        path, fl[0][0], fl[-1][0], len(fl), len(hi), len(fz), len(fl) - len(hi) - len(fz),
        mean([r[3] for r in hi]), mean([r[3] for r in fz]), mean([r[5] for r in fz]), mean([r[7] for r in fl])))
    for c in runs:
        print('   flat run t=%d len=%d s  sd_wall mean %.2f max %d  sd_cpu %.2f  vi/s %.1f  load1 %.2f' % (
            c[0][0], len(c), mean([r[3] for r in c]), max(r[4] for r in c), mean([r[5] for r in c]), mean([r[1] for r in c]), mean([r[7] for r in c])))
    print('   flat runs: %d, total %d s' % (len(runs), sum(len(c) for c in runs)))
