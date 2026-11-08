#!/usr/bin/env python3
"""s6963 G1e: same-run A/B of ROGUESQ_G1E_CELLIDX=tog (index on/off in BLK-second blocks). Joins each [g1b] second with the on state of
the latest [g1e-cell] line in log order (seconds next to a block edge are dropped), and with [g1b-gt] thread 8 cpu (the game thread).
Per state: seconds, mean tasks/s, slow seconds (<=57), mean/max game-thread cpu ms/s, walk iterations/s, idx hits+misses/s.
Also prints CHECK totals (tot_chk, tot_bad = real mismatches, flip/flipbad = positive control: flipbad must equal flip).
usage: g1e_cellidx_ab.py LOG [--t0 120]"""
import re, sys, argparse, statistics as st
ap = argparse.ArgumentParser(); ap.add_argument('log'); ap.add_argument('--t0', type=int, default=120); a = ap.parse_args()
on = None; rows = []; gt = {}; cell = None; last = None; edge = set()
for l in open(a.log, errors='replace'):
    if l.startswith('[g1e-cell] s='):
        d = dict(re.findall(r'(\w+)=(\d+)', l)); n = int(d['on'])
        cell = d; last = d
        if on is not None and n != on: edge.add(len(rows))
        on = n
    elif l.startswith('[g1b] t='):
        d = dict(re.findall(r'(\w+)=([\d.]+)', l)); rows.append((int(d['t']), int(d['tasks']), on, dict(cell) if cell else {}))
    elif l.startswith('[g1b-gt] t='):
        t = int(re.search(r't=(\d+)', l).group(1)); m = re.search(r' 8\.\d+:(\d+)/', l); gt[t] = int(m.group(1)) if m else 0
bad = set()
for i in edge: bad |= {i - 1, i, i + 1}
G = {}
for i, (t, k, o, c) in enumerate(rows):
    if t < a.t0 or o is None or i in bad: continue
    G.setdefault(o, []).append((t, k, gt.get(t, 0), int(c.get('it', 0)), int(c.get('ihit', 0)) + int(c.get('imiss', 0)), int(c.get('calls', 0))))
print('on | secs | tasks mean | slow<=57 | min | gcpu mean | gcpu max | walk it/s | idx ans/s | calls/s')
for o in sorted(G):
    v = G[o]; f = lambda j: [x[j] for x in v]
    print(f"{o} | {len(v)} | {st.mean(f(1)):.2f} | {sum(1 for x in v if x[1] <= 57)} | {min(f(1))} | {st.mean(f(2)):.0f} | {max(f(2))} | {st.mean(f(3)):.0f} | {st.mean(f(4)):.0f} | {st.mean(f(5)):.0f}")
if last: print('last cell line:', {k: last[k] for k in ('tot_chk', 'tot_bad', 'flip', 'flipbad', 'maxchain', 'idx') if k in last})
