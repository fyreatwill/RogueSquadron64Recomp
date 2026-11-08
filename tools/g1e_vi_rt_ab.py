#!/usr/bin/env python3
"""s6967 G1e: per-block A/B for ROGUESQ_VI_RT_TOGGLE (VI thread Mach real-time policy on/off). Blocks come from TL mark 16
(arg = state, ROGUESQ_G1E_TL); TL and present-ring clocks are the same (mach, s6967 offset 0). Per block:
  vlat  VI edge lateness vs its ideal deadline (total_vis * T, constant fitted as the run minimum), p50/p90, share >2 ms
  vi19  VI intervals >= 19 ms per s       miss  presents shown >= 25 ms after the previous one, per s
  lat   present latency p50 (same basis as g1e_drain_blocks.py: presentedTime - Q + tp)   acq>5  share of Q with acq_ms > 5
  drops D rows (drain drops) per block
usage: g1e_vi_rt_ab.py tl.bin.<pid> ring.txt [--from 95]"""
import sys, struct, bisect, statistics as st
args = sys.argv[1:]; frm = 95.0
if '--from' in args: i = args.index('--from'); frm = float(args[i + 1]); del args[i:i + 2]
pc = lambda v, p: sorted(v)[int(p * (len(v) - 1))] if v else float('nan')
raw = open(args[0], 'rb').read(); n = len(raw) // 24
ev = sorted(struct.unpack_from('<qIIii', raw, i * 24) for i in range(n)); ev = [e for e in ev if e[0]]
T = 1e6 / 60
vi = [(e[0] / 1e6, e[2]) for e in ev if e[1] == 1]
flips = [(e[0] / 1e6, e[2]) for e in ev if e[1] == 16]
if not flips: sys.exit('no TL mark 16: toggle not active (control failed)')
t_first = vi[0][0]
m = min(t * 1e6 - k * T for t, k in vi if t - t_first > 30)
Q = {}; P = []; D = []
for l in open(args[1], errors='replace'):
    p = l.split()
    if len(p) < 2 or not l.endswith('\n'): continue
    kv = dict(x.split('=', 1) for x in p[2:] if '=' in x)
    try:
        if p[0] == 'D': D.append(float(p[1]))
        elif p[0] == 'Q' and kv.get('skip') == '0' and 'acq_ms' in kv: Q.setdefault(int(kv['mtl']), (float(p[1]), float(kv['acq_ms']), float(kv['tp_ms'])))
        elif p[0] == 'P' and float(kv.get('at', 0)) > 0: P.append((float(kv['at']), int(kv['mtl'])))
    except (KeyError, ValueError): pass
P.sort()
edges = flips + [(max(vi[-1][0], P[-1][0] if P else 0), -1)]
if flips[0][0] - t_first > frm + 5: edges = [(t_first + frm, 1 - flips[0][1])] + edges  # ROGUESQ_VI_RT_AT one-way flip: the before block
print('blk on |    t0..t1 | vlat p50 p90 >2ms% | vi19/s | miss/s | lat p50 | acq>5% | drops')
res = {0: [], 1: []}
for b in range(len(edges) - 1):
    a0, on = edges[b]; a1 = edges[b + 1][0]
    if a0 - t_first < frm or a1 - a0 < 5: continue
    V = [(t, k) for t, k in vi if a0 + 0.5 <= t < a1]
    vl = [(t * 1e6 - k * T - m) / 1e3 for t, k in V]
    d = [(y[0] - x[0]) * 1e3 for x, y in zip(V, V[1:])]
    PP = [x for x in P if a0 + 0.5 <= x[0] < a1]
    dp = [(y[0] - x[0]) * 1e3 for x, y in zip(PP, PP[1:])]
    lat = [(at - Q[mm][0]) * 1e3 + Q[mm][2] for at, mm in PP if mm in Q]
    QQ = [q for q in Q.values() if a0 + 0.5 <= q[0] < a1]
    dur = a1 - a0 - 0.5
    r = dict(v50=pc(vl, .5), v90=pc(vl, .9), v2=100 * sum(x > 2 for x in vl) / max(1, len(vl)), vi19=sum(x >= 19 for x in d) / dur,
             miss=sum(x >= 25 for x in dp) / dur, lat=pc(lat, .5), a5=100 * sum(q[1] > 5 for q in QQ) / max(1, len(QQ)), dr=sum(a0 <= x < a1 for x in D))
    res[on].append(r)
    print('%3d %2d | %5.0f..%5.0f | %5.2f %5.2f %5.1f | %6.2f | %6.2f | %7.1f | %6.1f | %d' % (b, on, a0 - t_first, a1 - t_first, r['v50'], r['v90'], r['v2'], r['vi19'], r['miss'], r['lat'], r['a5'], r['dr']))
for on in (0, 1):
    R = res[on]
    if R: print('on=%d blocks %d: vlat p90 median %.2f, >2ms %.1f%%, vi19/s %.2f, miss/s %.2f, lat p50 median %.1f (%.1f..%.1f), acq>5%% median %.1f, blocks at level (acq>5%%>30) %d, drops %d'
                % (on, len(R), st.median(r['v90'] for r in R), st.median(r['v2'] for r in R), st.median(r['vi19'] for r in R), st.median(r['miss'] for r in R),
                   st.median(r['lat'] for r in R), min(r['lat'] for r in R), max(r['lat'] for r in R), st.median(r['a5'] for r in R), sum(r['a5'] > 30 for r in R), sum(r['dr'] for r in R)))
