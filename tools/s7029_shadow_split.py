#!/usr/bin/env python3
"""s7029 G1c (g1c-bump-push-split): same-run 3-way split of ROGUESQ_G1E_BUMPFAST=2 + ROGUESQ_G1E_BUMPFAST_SH=tog3 (mach second % 3 ->
shadow as is / reserve vectors from previous peaks / no S4272 shadow, diagnostic) from the ROGUESQ_G1E_TRING ring (38 cols: s7028's 35 +
s7029 per-row task counts of shadow arms 0/1/2). self_net = submit(x16) + commit - RT64 handoff - record_submit - AQ_NULL offset.
usage: s7029_shadow_split.py RING [--t0-s 30]
Arm control: plain-counter tasks (col 33) > 0 on every row. Timing control: spin_win=1 rows read rt/handoff +~spin.
Discriminator (spin_win=0): (asis - reserve)/asis_net or (asis - noshadow)/asis_net >= 40% of the s7028 10.7 ns remainder -> H-shadow,
else H-call (call overhead + range push)."""
import sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument('ring'); ap.add_argument('--t0-s', type=float, default=30.0)
a = ap.parse_args()
R = []
for l in open(a.ring):
    if l.startswith('#'): continue
    f = l.split()
    if len(f) < 38: continue
    t, w, c, uc, sub, com = map(float, f[:6]); calls, by, n, ph = map(int, f[6:10])
    rt_n = int(f[20]); rt = float(f[21]) / 1e3; rec = float(f[24]) / 1e3; sw = int(f[28])
    on2 = int(f[33]); fast = int(f[31]); nul = float(f[34]); s0, s1, s2 = map(int, f[35:38])
    R.append(dict(t=t, w=w, sub=sub, com=com, calls=calls, n=n, ph=ph, rt_n=rt_n, rt=rt, rec=rec, by=by,
                  self=sub + com - rt - rec, nul=nul, sw=sw, on2=on2, fast=fast, s=(s0, s1, s2)))
print(f"rows={len(R)}")
if not R: sys.exit(1)
for i, r in enumerate(R): r['dt'] = (r['t'] - R[i - 1]['t']) if i else 0.0
tmin = R[0]['t'] + a.t0_s * 1000
ph = {}
for r in R:
    if r['t'] >= tmin and r['calls'] > 1000: ph[r['ph']] = ph.get(r['ph'], 0) + 1
fph = max(ph, key=ph.get)
F = [r for r in R if r['t'] >= tmin and r['ph'] == fph and r['n'] == 1 and r['dt'] < 200 and r['calls'] > 1000]
print(f"flight phase={fph} rows={len(F)} plain-counter rows={sum(1 for r in F if r['on2'] > 0)}")
names = ('asis', 'reserve', 'noshadow')
def arm(r):
    k = [names[i] for i in range(3) if r['s'][i] > 0]
    return k[0] if len(k) == 1 else 'mix'
for r in F: r['arm'] = arm(r)
m = lambda g, k: sum(r[k] for r in g) / len(g) if g else float('nan')
print("arm       sw rows  bumps/task  fast/bump  self_ms  null_ms  net_ns/b  rt_us/handoff  sd_wall  fps")
res = {}
for A in names:
    for sw in (0, 1):
        g = [r for r in F if r['arm'] == A and r['sw'] == sw]
        if not g: continue
        b = m(g, 'calls'); fpb = sum(r['fast'] for r in g) / max(1, sum(r['calls'] for r in g))
        ns = m(g, 'self') * 1e6 / b; nn = m(g, 'nul') * 1e6 / b
        rth = sum(r['rt'] for r in g) * 1e3 / max(1, sum(r['rt_n'] for r in g)); fps = 1000.0 / m(g, 'dt')
        res[(A, sw)] = dict(net=ns - nn, nn=nn, w=m(g, 'w'), fps=fps, self=m(g, 'self'))
        print(f"{A:9} {sw:2} {len(g):5}  {b:9.0f}  {fpb:8.3f}  {m(g,'self'):7.3f}  {m(g,'nul'):7.3f}  {ns-nn:8.2f}  {rth:12.2f}  {m(g,'w'):7.3f}  {fps:5.1f}")
print(f"mixed rows dropped: {sum(1 for r in F if r['arm']=='mix')}")
if all((k, 0) in res for k in names):
    o, rv, ns_ = (res[(k, 0)] for k in names)
    print(f"net ns/bump asis {o['net']:.2f} reserve {rv['net']:.2f} noshadow {ns_['net']:.2f}")
    print(f"reserve saves {o['net']-rv['net']:.2f} ns/bump, shadow total {o['net']-ns_['net']:.2f} ns/bump ({(o['net']-ns_['net'])/o['net']*100:.1f}% of asis net)")
    print(f"self ms/task asis {o['self']:.3f} reserve {rv['self']:.3f} noshadow {ns_['self']:.3f}")
    REM = 10.7
    v = []
    if (o['net'] - rv['net']) >= 0.4 * REM: v.append('H-shadow (allocation: reserve pays)')
    if (o['net'] - ns_['net']) >= 0.4 * REM: v.append('H-shadow (shadow copy/bookkeeping)')
    print("verdict:", ' + '.join(v) or 'H-call (shadow < 40% of the remainder)')
