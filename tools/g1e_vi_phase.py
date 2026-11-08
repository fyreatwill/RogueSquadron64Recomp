#!/usr/bin/env python3
"""s6987 G1e: for each present (late 30-40 ms on-glass interval vs normal 15-18.5 ms), the phase of the guest VI that
produced it relative to the on-glass display vsync grid (P row at), the VI->commit time, and the vsync-grid residual
around the present (H-vi-slip vs H-vsync-jitter vs H-pre-Q). Chain: P(mtl) -> Q(mtl) -> last W before Q -> last kick
(tl code 5 arg 1) before W -> last VI (tl code 1) before the kick. Clocks: tl steady us + G-row offset (as g1e_late_leg).
usage: g1e_vi_phase.py tl.bin.<pid> gring.txt ring.txt [--from S]"""
import sys, struct, bisect, collections, statistics as st
args = sys.argv[1:]; t_from = 95.0
if '--from' in args: i = args.index('--from'); t_from = float(args[i + 1]); del args[i:i + 2]
tlf, gf, rf = args
pc = lambda v, p: sorted(v)[int(p * (len(v) - 1))] if v else float('nan')
off = []
for l in open(gf, errors='replace'):
    if l.startswith('G ') and ' us=' in l and l.endswith('\n'):
        p = l.split(); us = int(next(x for x in p if x.startswith('us='))[3:]); off.append(float(p[1]) - us / 1e6)
o = st.median(off)
raw = open(tlf, 'rb').read(); n = len(raw) // 24
ev = sorted((r[0] / 1e6 + o, r[1], r[2]) for r in (struct.unpack_from('<qIIii', raw, i * 24) for i in range(n)))
ev = [e for e in ev if e[0] > o + 1]
vis = [e[0] for e in ev if e[1] == 1]; kt = [e[0] for e in ev if e[1] == 5 and e[2] == 1]
Q = {}; S = {}; P = []; W = []; WK = {}
for l in open(rf, errors='replace'):
    p = l.split()
    if len(p) < 3 or not l.endswith('\n'): continue
    kv = dict(x.split('=', 1) for x in p[2:] if '=' in x)
    try:
        if p[0] == 'Q' and kv.get('skip') == '0': Q[int(kv['mtl'])] = float(p[1])
        elif p[0] == 'S' and 'c' in kv: S[int(kv['mtl'])] = float(kv['c'])
        elif p[0] == 'P' and float(kv.get('at', 0)) > 0: P.append((float(kv['at']), int(kv['mtl'])))
        elif p[0] == 'W': W.append(float(p[1])); WK[float(p[1])] = kv  # s6987 wk/lk/pid/rs/qos fields
    except (KeyError, ValueError): pass
P.sort(); W.sort(); at = [x[0] for x in P]; t0 = at[0]
iv = sorted(b - a for a, b in zip(at, at[1:]) if 0.0155 < b - a < 0.0178); per = iv[len(iv) // 2]
# VI period and clock sanity
viv = sorted(b - a for a, b in zip(vis, vis[1:]) if 0.010 < b - a < 0.025)
print(f'vsync period {per*1e3:.4f} ms ({len(at)} P); VI period p50 {viv[len(viv)//2]*1e3:.4f} ms ({len(vis)} VI); G-row offset {o:.6f}')
# grid residual: fold every on-glass time onto the vsync phase of a running reference (local phase, robust to slow drift)
def gph(t):  # phase of t (ms) after the last on-glass vsync, folded by period
    k = bisect.bisect_right(at, t) - 1
    return ((t - at[k]) % per) * 1e3 if k >= 0 else float('nan')
rows = {'late': [], 'norm': []}
for j in range(2, len(P) - 2):
    d = (P[j][0] - P[j - 1][0]) * 1e3; m = P[j][1]
    key = 'late' if 30 <= d < 40 else ('norm' if 15 < d < 18.5 else None)
    if not key or m not in Q or m not in S or P[j][0] - t0 < t_from: continue
    w = bisect.bisect_right(W, Q[m]) - 1
    if w < 0: continue
    k = bisect.bisect_right(kt, W[w]) - 1
    if k < 0: continue
    v = bisect.bisect_right(vis, kt[k]) - 1
    if v < 0: continue
    vt = vis[v]; c = S[m]
    # local grid jitter: residual of the 4 surrounding P intervals from integer multiples of per
    jit = max(abs(((P[x + 1][0] - P[x][0]) / per - round((P[x + 1][0] - P[x][0]) / per)) * per * 1e3) for x in range(j - 2, j + 2))
    rows[key].append(dict(viph=gph(vt), vic=(c - vt) * 1e3, cph=gph(c), vik=(kt[k] - vt) * 1e3, kc=(c - kt[k]) * 1e3,
                          vivi=(vt - vis[v - 1]) * 1e3 if v else float('nan'), jit=jit, t=P[j][0] - t0, d=d))
L, N = rows['late'], rows['norm']
print(f'late {len(L)} normal {len(N)}')
print('  field   late p10/p50/p90        | normal p10/p50/p90')
for f in ('viph', 'vik', 'kc', 'vic', 'cph', 'vivi', 'jit'):
    a = [r[f] for r in L]; b = [r[f] for r in N]
    print(f'  {f:5s} ' + ' '.join(f'{pc(a, q):7.2f}' for q in (.1, .5, .9)) + '  | ' + ' '.join(f'{pc(b, q):7.2f}' for q in (.1, .5, .9)))
def auc(a, b): return sum((x > y) + 0.5 * (x == y) for x in a for y in b) / (len(a) * len(b)) if a and b else float('nan')
Ns = N[::max(1, len(N) // 3000)]
print('  AUC late>normal: ' + ' '.join(f"{f}={auc([r[f] for r in L], [r[f] for r in Ns]):.2f}" for f in ('viph', 'vik', 'kc', 'vic', 'cph', 'jit')))
for nm, R in rows.items():
    h = collections.Counter(int(r['viph'] // 2) * 2 for r in R)
    print(f'  {nm:4s} VI phase hist (2 ms bins): ' + ' '.join(f'{b:02d}:{h[b]}' for b in range(0, 18, 2)))

# --- s6987 corrected chain: W -> the send_dl return (gring R row) that preceded it -> that send_dl's kick -> its VI.
# The chain above attributes W to the last kick before W, which on lates is the NEXT frame's kick (kc ~5 ms < sd).
RR = sorted((float(l.split()[1]), float(l.split()[2][3:])) for l in open(gf, errors='replace') if l.startswith('R ') and ' sd=' in l and l.endswith('\n'))
Rt = [r[0] for r in RR]
rows2 = {'late': [], 'norm': []}
for j in range(2, len(P) - 2):
    d = (P[j][0] - P[j - 1][0]) * 1e3; m = P[j][1]
    key = 'late' if 30 <= d < 40 else ('norm' if 15 < d < 18.5 else None)
    if not key or m not in Q or m not in S or P[j][0] - t0 < t_from: continue
    w = bisect.bisect_right(W, Q[m]) - 1
    if w < 1: continue
    r = bisect.bisect_right(Rt, W[w]) - 1
    if r < 1: continue
    rt, sd = RR[r]; k = bisect.bisect_right(kt, rt - sd / 1e3 + 0.0005) - 1
    if k < 0: continue
    v = bisect.bisect_right(vis, kt[k]) - 1
    if v < 0: continue
    vt = vis[v]; c = S[m]
    rows2[key].append(dict(viph=gph(vt), ksd=(rt - kt[k]) * 1e3, rw=(W[w] - rt) * 1e3, busy=(W[w - 1] - rt) * 1e3,
                           ww=(W[w] - W[w - 1]) * 1e3, wq=(Q[m] - W[w]) * 1e3, qc=(c - Q[m]) * 1e3, vic=(c - vt) * 1e3,
                           wph=gph(W[w]), cph=gph(c), nk=bisect.bisect_right(kt, W[w]) - 1 - k, t=P[j][0] - t0))
    wk = WK.get(W[w], {})
    if 'wk' in wk:  # s6987 split of rw: R -> cursor wake (pick), mutex (mtx), presentId wait (pidw), setup, render (frame 0)
        f_ = {x: float(wk[x]) for x in ('wk', 'lk', 'pid', 'rs')}
        rows2[key][-1].update(pick=rows2[key][-1]['rw'] - f_['wk'], mtx=f_['wk'] - f_['lk'], pidw=f_['lk'] - f_['pid'],
                              setup=f_['pid'] - f_['rs'], rend=f_['rs'], wqos=float(wk.get('qos', 'nan')))
L2, N2 = rows2['late'], rows2['norm']; N2s = N2[::max(1, len(N2) // 3000)]
print(f'corrected chain: late {len(L2)} normal {len(N2)}')
ws_ = [x for x in L2 + N2 if 'pick' in x]  # positive control: the split must sum back to rw
if ws_: print(f"  split control: max |pick+mtx+pidw+setup+rend - rw| = {max(abs(x['pick']+x['mtx']+x['pidw']+x['setup']+x['rend']-x['rw']) for x in ws_):.4f} ms over {len(ws_)}")
for f in ('viph', 'ksd', 'rw', 'pick', 'mtx', 'pidw', 'setup', 'rend', 'wqos', 'busy', 'ww', 'wq', 'qc', 'vic', 'wph', 'cph', 'nk'):
    a = [x[f] for x in L2 if f in x]; b = [x[f] for x in N2 if f in x]
    if not a or not b: continue
    print(f'  {f:5s} ' + ' '.join(f'{pc(a, q):7.2f}' for q in (.1, .5, .9)) + '  | ' + ' '.join(f'{pc(b, q):7.2f}' for q in (.1, .5, .9))
          + f'  AUC {auc(a, [x[f] for x in N2s if f in x]):.2f}')

