#!/usr/bin/env python3
"""s6696 G3d: fold a ROGUESQ_G3D_LEGACY_TOGGLE run. Each [g1b] second and each [g3c] present stamp is assigned the latest
[g3d] legacy state by log order; the first [g1b] second after a flip is dropped (mixed). Flight only: [g1b] seconds with
tasks>0 after the first --skip seconds. Prints per arm: n, VI/s, game tasks/s, send_dl ms/task (wall, cpu), and present
interval p50/p95 plus the fraction of intervals <2 ms (bunched presents) and >50 ms (long gaps).
usage: g3d_toggle_fold.py run.log [--skip 60]"""
import sys, re, statistics as st
args = sys.argv[1:]; skip = 60
if '--skip' in args: i = args.index('--skip'); skip = int(args[i + 1]); del args[i:i + 2]
state = None; fresh = False; g1b = {0: [], 1: [], None: []}; dt = {0: [], 1: [], None: []}; last_t = None; flips = 0
rg = re.compile(r'^\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+) sd_wall=([\d.]+)/\d+ sd_cpu=([\d.]+)/')
for ln in open(args[0], errors='replace'):
    if ln.startswith('[g3d] legacy='):
        state = int(ln.split('legacy=')[1].split()[0]); fresh = True; last_t = None; flips += 1; continue
    m = rg.match(ln)
    if m:
        t, vi, tk, w, c = int(m[1]), int(m[2]), int(m[3]), float(m[4]), float(m[5])
        if fresh: fresh = False; continue
        if t >= skip and tk > 0: g1b[state].append((vi, tk, w, c))
        continue
    if ln.startswith('[g3c] vi='):
        t = float(ln.split(' t=')[1].split()[0])
        if last_t is not None: dt[state].append((t - last_t) * 1000.0)
        last_t = t
print(f'flips={flips}')
for s, name in ((0, 'fixed'), (1, 'legacy'), (None, 'pre-toggle')):
    r = g1b[s]
    if not r: print(f'{name}: no g1b seconds'); continue
    d = sorted(dt[s]); q = lambda p: d[min(len(d) - 1, int(p * len(d)))] if d else float('nan')
    print(f'{name}: n={len(r)} vi/s={st.mean(x[0] for x in r):.1f} tasks/s={st.mean(x[1] for x in r):.1f} '
          f'sd_wall={st.mean(x[2] for x in r):.1f}ms sd_cpu={st.mean(x[3] for x in r):.1f}ms | present dt n={len(d)} '
          f'p50={q(.5):.1f} p95={q(.95):.1f}ms <2ms={sum(x < 2 for x in d) / max(1, len(d)):.2f} >50ms={sum(x > 50 for x in d) / max(1, len(d)):.2f}')
