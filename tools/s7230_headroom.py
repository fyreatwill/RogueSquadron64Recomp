#!/usr/bin/env python3
"""s7230: owner-path frame headroom per arm, from ROGUESQ_G1B=1 [g1b] lines (format: see tools/s7229_flat30_cost.py).
usage: s7230_headroom.py [--win 77-97] LOG [LOG...]   (LOG may be .zst)
Per arm, over flight (from the first second with tasks>=45): seconds <55 tasks/s, seconds whose per-second MAX gfx task
wall >= 16.7 ms (a frame that missed its VI), p50/p95/max of the per-second mean sd_wall, the heaviest 20-s rolling window
(start, mean sd_wall, tasks/s) and the fixed --win window. Headroom = 16.7 - heaviest-window mean sd_wall."""
import sys, re, subprocess
R = re.compile(r'^\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+) sd_wall=([0-9.]+)/(\d+) sd_cpu=([0-9.]+)/(\d+).*?load1=([0-9.]+)')
args = sys.argv[1:]; w0, w1 = 77, 97
if args and args[0] == '--win': w0, w1 = map(int, args[1].split('-')); args = args[2:]
def lines(p):
    if p.endswith('.zst'): return subprocess.run(['zstd', '-dc', p], capture_output=True).stdout.decode('utf8', 'replace').splitlines()
    return open(p, errors='replace').read().splitlines()
mean = lambda v: sum(v) / len(v) if v else float('nan')
for p in args:
    rows = [tuple(float(x) for x in m.groups()) for m in (R.match(l) for l in lines(p)) if m]
    f = next((i for i, r in enumerate(rows) if r[2] >= 45), None)
    if f is None: print(p, 'no flight (%d g1b rows)' % len(rows)); continue
    fl = rows[f:]; sd = sorted(r[3] for r in fl)
    low = sum(r[2] < 55 for r in fl); miss = sum(r[4] >= 17 for r in fl)
    best = max(((mean([r[3] for r in fl[i:i+20]]), fl[i][0], mean([r[2] for r in fl[i:i+20]])) for i in range(max(1, len(fl) - 19))))
    win = [r for r in fl if w0 <= r[0] <= w1]
    print('%s: t=%d..%d n=%d <55/s:%d max>=17ms:%d sd_wall p50 %.2f p95 %.2f max %.2f | heaviest20 t=%d %.2f ms %.1f/s headroom %.2f ms | win%d-%d %.1f/s %.2f ms | load1 %.2f' % (
        p, fl[0][0], fl[-1][0], len(fl), low, miss, sd[len(sd)//2], sd[int(len(sd)*.95)], sd[-1], best[1], best[0], best[2],
        16.7 - best[0], w0, w1, mean([r[2] for r in win]), mean([r[3] for r in win]), mean([r[7] for r in fl])))
