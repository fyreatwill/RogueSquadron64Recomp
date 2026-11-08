#!/usr/bin/env python3
"""s6954 G1e: per-task split of the dd4 tail from the ROGUESQ_G1E_TRING ring (ROGUESQ_G1E_AQ=3 ROGUESQ_G1B=1).
usage: g1e_task_ring.py RING LOG [--t0 100] [--spin 20]
Row: t_ms sd_wall sd_cpu ucode_ms submit_ms(sampled x16) commit_ms calls rdp_bytes n_ucode phase spin.
Terms per task: uc_x = ucode - submit (LLE interpreter), sub = sampled rsp_dpc_submit, com = task-end commit (defer_end),
rt64 = sd_cpu - ucode - commit (RT64 send_dl remainder on the Gfx thread), gap = sd_wall - sd_cpu (descheduled/blocked).
Control A: per-second ring mean sd_wall vs the [g1b] sd_wall of the same second (same clock), must agree within 5%.
Control B: spin windows (SPIN_NS>0 on every submit call): sub and sd_wall must both rise by ~calls*spin.
Split: flight no-spin tasks, slowest 10% by sd_wall vs the 40-60th percentile band; each term's delta and share."""
import re, sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument('ring'); ap.add_argument('log'); ap.add_argument('--t0', type=float, default=100)
a = ap.parse_args()
R = []
for l in open(a.ring):
    if l.startswith('#'): continue
    f = l.split()
    if len(f) != 11: continue
    t, w, c, uc, sub, com = map(float, f[:6]); calls, by, n, ph, sp = map(int, f[6:])
    R.append(dict(t=t, w=w, c=c, uc=uc, sub=sub, com=com, calls=calls, by=by, n=n, ph=ph, sp=sp,
                  ucx=uc - sub, rt=c - uc - com, gap=w - c))
g1b = {}
for l in open(a.log, errors='replace'):
    if l.startswith('[g1b] '):
        d = dict(re.findall(r'(\w+)=([\d./]+)', l)); g1b[int(d['t'])] = (int(d['tasks']), float(d['sd_wall'].split('/')[0]))
# Control A
per = {}
for r in R: per.setdefault(int(r['t'] // 1000), []).append(r['w'])
sa = sb = 0.0; k = 0; worst = 0.0
for s, ws in per.items():
    if s in g1b and g1b[s][0] == len(ws) and len(ws) > 5:
        m = sum(ws) / len(ws); sa += m; sb += g1b[s][1]; k += 1; worst = max(worst, abs(m - g1b[s][1]) / max(g1b[s][1], 1e-9))
print(f"controlA seconds_matched={k} ring_mean={sa/max(k,1):.3f} g1b_mean={sb/max(k,1):.3f} ratio={sa/max(sb,1e-9):.4f} worst_sec_rel={worst:.4f}")
nmulti = sum(1 for r in R if r['n'] != 1); print(f"rows={len(R)} rows_with_n_ucode!=1={nmulti}")
ph = {}
for r in R:
    if r['t'] >= a.t0 * 1000: ph[r['ph']] = ph.get(r['ph'], 0) + 1
fph = max(ph, key=ph.get) if ph else -1
F = [r for r in R if r['t'] >= a.t0 * 1000 and r['ph'] == fph and r['n'] == 1]
K = ['w', 'c', 'gap', 'ucx', 'sub', 'com', 'rt', 'calls', 'by']
m = lambda g, k: sum(r[k] for r in g) / len(g) if g else float('nan')
def row(name, g): print(f"{name:10}" + ''.join(f"{m(g,k):10.3f}" if k not in ('calls', 'by') else f"{m(g,k):10.0f}" for k in K) + f"  n={len(g)}")
# Control B
on = [r for r in F if r['sp'] > 0]; off = [r for r in F if r['sp'] == 0]
print(f"flight phase={fph} tasks={len(F)} spin_on={len(on)} spin_off={len(off)}")
print(' ' * 10 + ''.join(f"{k:>10}" for k in K))
if on:
    row('spin_on', on); row('spin_off', off)
    exp = m(on, 'calls') * on[0]['sp'] / 1e6
    print(f"controlB expected_add~{exp:.3f} ms (calls*spin, plus clock reads)  d_sub={m(on,'sub')-m(off,'sub'):.3f}  d_wall={m(on,'w')-m(off,'w'):.3f}  d_ucx={m(on,'ucx')-m(off,'ucx'):.3f}")
G = sorted(off, key=lambda r: r['w']); n = len(G)
if n < 50: sys.exit('too few no-spin flight tasks')
slow = G[int(n * .9):]; mid = G[int(n * .4):int(n * .6)]
row('slow10%', slow); row('mid40-60', mid)
dw = m(slow, 'w') - m(mid, 'w')
print('delta     ' + ''.join(f"{m(slow,k)-m(mid,k):10.3f}" for k in K))
print('share     ' + ''.join(f"{(m(slow,k)-m(mid,k))/dw:10.2f}" if k in ('c', 'gap', 'ucx', 'sub', 'com', 'rt') else ' ' * 10 for k in K))
def corr(x, y):
    nn = len(x); mx = sum(x) / nn; my = sum(y) / nn
    cv = sum((p - mx) * (q - my) for p, q in zip(x, y)); vx = sum((p - mx) ** 2 for p in x); vy = sum((q - my) ** 2 for q in y)
    return cv / (vx * vy) ** .5 if vx and vy else 0.0
W = [r['w'] for r in off]
print('r(sd_wall)' + ''.join(f"{corr(W,[r[k] for r in off]):10.3f}" for k in K))
# per-call cost: does the submit term scale with calls (H-submit per-call) or with bytes?
for nm, g in (('slow', slow), ('mid', mid)):
    print(f"{nm}: sub_us_per_call={1e3*m(g,'sub')/max(m(g,'calls'),1):.4f} ucx_us_per_call={1e3*m(g,'ucx')/max(m(g,'calls'),1):.4f} rt_ms_per_MB={m(g,'rt')/max(m(g,'by')/1e6,1e-9):.3f} bytes/call={m(g,'by')/max(m(g,'calls'),1):.1f}")
