#!/usr/bin/env python3
"""s6955 G1e: per-arm split of a ROGUESQ_G1E_BATCH=tog run from the ROGUESQ_G1E_TRING ring (13-column rows, AQ=3).
usage: g1e_batch_arms.py RING [--t0 100] [--arm batch|cdiag]
s6956: 14-column rows add the cdiag arm (ROGUESQ_G1E_CDIAG); --arm cdiag splits by it.
Rows: t sd_wall sd_cpu ucode submit(x16 sampled) commit calls bytes n_ucode phase spin batch ranges.
Flight = most common phase after t0, n_ucode==1, spin 0. Arms by the batch column. Adjacent 10 s blocks (by t) give paired deltas.
Positive control: ranges per task must drop in batch=1 tasks while calls per task stay comparable."""
import sys, argparse, statistics as st
ap = argparse.ArgumentParser(); ap.add_argument('ring'); ap.add_argument('--t0', type=float, default=100); ap.add_argument('--arm', default='batch'); a = ap.parse_args()
R = []
for l in open(a.ring):
    if l.startswith('#'): continue
    f = l.split()
    if len(f) not in (13, 14): continue
    t, w, c, uc, sub, com = map(float, f[:6]); calls, by, n, ph, sp, bt, rg = map(int, f[6:13]); cd = int(f[13]) if len(f) == 14 else -1
    b = cd if a.arm == 'cdiag' else bt
    R.append(dict(t=t, w=w, c=c, uc=uc, sub=sub, com=com, calls=calls, by=by, n=n, ph=ph, sp=sp, b=b, rg=rg, ucx=uc - sub, rt=c - uc - com))
ph = {}
for r in R:
    if r['t'] >= a.t0 * 1000: ph[r['ph']] = ph.get(r['ph'], 0) + 1
fph = max(ph, key=ph.get)
F = [r for r in R if r['t'] >= a.t0 * 1000 and r['ph'] == fph and r['n'] == 1 and r['sp'] == 0]
K = ['w', 'c', 'uc', 'ucx', 'sub', 'com', 'rt', 'calls', 'rg', 'by']
print(f"flight phase={fph} tasks={len(F)}")
print(' ' * 8 + ''.join(f"{k:>10}" for k in K) + '      n')
for arm in (0, 1):
    g = [r for r in F if r['b'] == arm]
    if not g: continue
    print(f"arm{arm} md" + ''.join(f"{st.median(r[k] for r in g):10.3f}" if k not in ('calls', 'rg', 'by') else f"{st.median(r[k] for r in g):10.0f}" for k in K) + f"  {len(g)}")
    print(f"arm{arm} mn" + ''.join(f"{st.mean(r[k] for r in g):10.3f}" if k not in ('calls', 'rg', 'by') else f"{st.mean(r[k] for r in g):10.0f}" for k in K))
# block pairs: consecutive runs of same arm
blocks = []
for r in F:
    if blocks and blocks[-1][0] == r['b'] and r['t'] - blocks[-1][1][-1]['t'] < 3000: blocks[-1][1].append(r)
    else: blocks.append((r['b'], [r]))
blocks = [(b, g) for b, g in blocks if len(g) >= 100]
d = {k: [] for k in ('w', 'sub', 'com', 'ucx', 'rt')}
for (b1, g1), (b2, g2) in zip(blocks, blocks[1:]):
    if b1 == b2: continue
    on, off = (g1, g2) if b1 == 1 else (g2, g1)
    for k in d: d[k].append(st.mean(r[k] for r in on) - st.mean(r[k] for r in off))
for k, v in d.items():
    if v: print(f"pair d_{k} (on-off, ms/task) mean={st.mean(v):+.3f} sd={st.stdev(v) if len(v) > 1 else 0:.3f} lower={sum(x < 0 for x in v)}/{len(v)}")
