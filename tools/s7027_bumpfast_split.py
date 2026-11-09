#!/usr/bin/env python3
"""s7027 G1c (g1c-bump-fastpath): same-run split of a ROGUESQ_G1E_BUMPFAST=tog run from the ROGUESQ_G1E_TRING ring
(ROGUESQ_S7026_SUB=1 + the 4 s7027 columns bf_on bf_off bf_fast bf_slow = 33 columns).
usage: s7027_bumpfast_split.py RING [--t0-s 30]
Rows are classed by the per-task arm latched in rs64_dpc_defer_begin: on = only fast-arm tasks in the row, off = only
retail-path tasks. self = submit(x16 sampled) + commit - RT64 handoff - record_submit (bridge self, as s7026).
Arm control: on rows must show bf_fast > 0, off rows bf_fast == 0. Timing control: spin_win=1 rows (S7026_SPIN_NS after
every RT64 handoff) must show rt/handoff up by ~spin. Arm comparison uses spin_win=0 rows only.
Discriminator: bridge self ns/bump on vs off: >=50% cut = H-checks, <20% = H-push / H-cache."""
import sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument('ring'); ap.add_argument('--t0-s', type=float, default=30.0)
ap.add_argument('--spin-us', type=float, default=300.0)
a = ap.parse_args()
R = []
for l in open(a.ring):
    if l.startswith('#'): continue
    f = l.split()
    if len(f) < 33: continue
    t, w, c, uc, sub, com = map(float, f[:6]); calls, by, n, ph = map(int, f[6:10])
    cap0 = int(f[17]); rt_n = int(f[20]); rt = float(f[21]) / 1e3; rec = float(f[24]) / 1e3; sw = int(f[28])
    on, off, fast, slow = map(int, f[29:33])
    R.append(dict(t=t, w=w, uc=uc, sub=sub, com=com, calls=calls, by=by, n=n, ph=ph, cap=cap0, rt_n=rt_n, rt=rt, rec=rec,
                  self=sub + com - rt - rec, sw=sw, on=on, off=off, fast=fast, slow=slow))
print(f"rows={len(R)}")
if not R: sys.exit(1)
for i, r in enumerate(R): r['dt'] = (r['t'] - R[i - 1]['t']) if i else 0.0
tmin = R[0]['t'] + a.t0_s * 1000
ph = {}
for r in R:
    if r['t'] >= tmin and r['calls'] > 1000: ph[r['ph']] = ph.get(r['ph'], 0) + 1
fph = max(ph, key=ph.get)
F = [r for r in R if r['t'] >= tmin and r['ph'] == fph and r['n'] == 1 and r['dt'] < 200 and r['calls'] > 1000]
print(f"flight phase={fph} rows={len(F)}")
m = lambda g, k: sum(r[k] for r in g) / len(g) if g else float('nan')
def arm(g): return 'on' if all(r['on'] > 0 and r['off'] == 0 for r in [g]) else ('off' if g['off'] > 0 and g['on'] == 0 else 'mix')
for r in F: r['arm'] = arm(r)
print("arm sw rows  bumps/task  fast/bump  self_ms  self_ns/bump  sub_ms  rt_ms  rt_us/handoff  ucode_ms  sd_wall  fps")
res = {}
for A in ('off', 'on'):
    for sw in (0, 1):
        g = [r for r in F if r['arm'] == A and r['sw'] == sw]
        if not g: continue
        b = m(g, 'calls'); fpb = sum(r['fast'] for r in g) / max(1, sum(r['calls'] for r in g))
        ns = m(g, 'self') * 1e6 / b; rth = sum(r['rt'] for r in g) * 1e3 / max(1, sum(r['rt_n'] for r in g))
        fps = 1000.0 / m(g, 'dt')
        res[(A, sw)] = dict(ns=ns, w=m(g, 'w'), fps=fps, self=m(g, 'self'))
        print(f"{A:3} {sw:2} {len(g):5}  {b:9.0f}  {fpb:8.3f}  {m(g,'self'):7.3f}  {ns:11.2f}  {m(g,'sub'):6.3f}  {m(g,'rt'):5.3f}  {rth:12.2f}  {m(g,'uc'):8.3f}  {m(g,'w'):7.3f}  {fps:5.1f}")
print(f"mixed rows dropped: {sum(1 for r in F if r['arm']=='mix')}")
if ('off', 0) in res and ('on', 0) in res:
    o, n_ = res[('off', 0)], res[('on', 0)]
    cut = 1 - n_['ns'] / o['ns']
    print(f"self ns/bump off {o['ns']:.2f} -> on {n_['ns']:.2f}  cut {cut*100:.1f}%  self/task {o['self']:.3f} -> {n_['self']:.3f} ms  sd_wall {o['w']:.3f} -> {n_['w']:.3f}  fps {o['fps']:.1f} -> {n_['fps']:.1f}")
    print("verdict:", "H-checks" if cut >= 0.5 else ("H-push/H-cache (<20%)" if cut < 0.2 else "partial (20-50%)"))
