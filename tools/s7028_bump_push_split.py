#!/usr/bin/env python3
"""s7028 G1c (g1c-bump-push-split): same-run 3-way split of a ROGUESQ_G1E_BUMPFAST=tog3 run (mach second % 3 -> off / fast /
fast + plain per-task counters) from the ROGUESQ_G1E_TRING ring (S7026_SUB + s7027 4 cols + s7028 bf_on2 aq_null_ms = 35 cols).
usage: s7028_bump_push_split.py RING [--t0-s 30]
self = submit(x16) + commit - RT64 handoff - record_submit (as s7026/s7027). null = AQ_NULL empty-call timing (x16) per task:
self_net = self - null removes the per-timed-call clock offset (H-offset). Arms: off rows only off tasks, fast = only arm-1, plain =
only arm-2. Arm control: fast/bump == 0 on off rows, > 0 on fast and plain rows. Timing control: spin_win=1 rows rt/handoff +~spin.
Discriminator (spin_win=0): null/bump >= 5 ns -> H-offset; (fast - plain)/off >= 40% -> H-atomics; plain/off still >= 60% of off_net
with atomics small -> H-shadow (push/range/shadow insert carries the rest)."""
import sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument('ring'); ap.add_argument('--t0-s', type=float, default=30.0)
a = ap.parse_args()
R = []
for l in open(a.ring):
    if l.startswith('#'): continue
    f = l.split()
    if len(f) < 35: continue
    t, w, c, uc, sub, com = map(float, f[:6]); calls, by, n, ph = map(int, f[6:10])
    rt_n = int(f[20]); rt = float(f[21]) / 1e3; rec = float(f[24]) / 1e3; sw = int(f[28])
    on, off, fast, slow, on2 = map(int, f[29:34]); nul = float(f[34])
    R.append(dict(t=t, w=w, uc=uc, sub=sub, com=com, calls=calls, n=n, ph=ph, rt_n=rt_n, rt=rt, rec=rec,
                  self=sub + com - rt - rec, nul=nul, sw=sw, on=on, off=off, on2=on2, fast=fast, slow=slow))
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
def arm(r):
    k = [x for x, v in (('off', r['off']), ('fast', r['on']), ('plain', r['on2'])) if v > 0]
    return k[0] if len(k) == 1 else 'mix'
for r in F: r['arm'] = arm(r)
m = lambda g, k: sum(r[k] for r in g) / len(g) if g else float('nan')
print("arm   sw rows  bumps/task  fast/bump  self_ms  null_ms  self_ns/b  null_ns/b  net_ns/b  rt_us/handoff  sd_wall  fps")
res = {}
for A in ('off', 'fast', 'plain'):
    for sw in (0, 1):
        g = [r for r in F if r['arm'] == A and r['sw'] == sw]
        if not g: continue
        b = m(g, 'calls'); fpb = sum(r['fast'] for r in g) / max(1, sum(r['calls'] for r in g))
        ns = m(g, 'self') * 1e6 / b; nn = m(g, 'nul') * 1e6 / b
        rth = sum(r['rt'] for r in g) * 1e3 / max(1, sum(r['rt_n'] for r in g)); fps = 1000.0 / m(g, 'dt')
        res[(A, sw)] = dict(ns=ns, nn=nn, net=ns - nn, w=m(g, 'w'), fps=fps)
        print(f"{A:5} {sw:2} {len(g):5}  {b:9.0f}  {fpb:8.3f}  {m(g,'self'):7.3f}  {m(g,'nul'):7.3f}  {ns:9.2f}  {nn:9.2f}  {ns-nn:8.2f}  {rth:12.2f}  {m(g,'w'):7.3f}  {fps:5.1f}")
print(f"mixed rows dropped: {sum(1 for r in F if r['arm']=='mix')}")
if all((k, 0) in res for k in ('off', 'fast', 'plain')):
    o, fa, pl = res[('off', 0)], res[('fast', 0)], res[('plain', 0)]
    print(f"net ns/bump off {o['net']:.2f}  fast {fa['net']:.2f}  plain {pl['net']:.2f}  null {o['nn']:.2f}")
    print(f"checks share {(o['net']-fa['net'])/o['net']*100:.1f}%  atomics share {(fa['net']-pl['net'])/o['net']*100:.1f}%  remainder (push/shadow/call) {pl['net']/o['net']*100:.1f}%")
    print(f"fps off {o['fps']:.1f} fast {fa['fps']:.1f} plain {pl['fps']:.1f}; sd_wall {o['w']:.3f} {fa['w']:.3f} {pl['w']:.3f}")
    v = []
    if o['nn'] >= 5: v.append('H-offset')
    if (fa['net'] - pl['net']) / o['net'] >= 0.4: v.append('H-atomics')
    if pl['net'] / o['net'] >= 0.6: v.append('H-shadow (remainder)')
    print("verdict:", ' + '.join(v) or 'none above threshold')
