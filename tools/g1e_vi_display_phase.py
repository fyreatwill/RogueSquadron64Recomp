#!/usr/bin/env python3
"""s6968 G1e: does our VI grid drift in phase against the display vsync, and do 21:9 drawable-queue level onsets sit at a fixed
phase? (H-vsync-phase vs H-compositor vs H-gpu-late, scratch/agent/NEXT.md s6967).
Inputs: TL (ROGUESQ_G1E_TL, code 1 = VI edge, arg = total VIs; mach us, same clock as the ring) and the present ring
(Q rows: submit, acq/tp/gpu ms; P rows: at = presentedTime = a display vsync). Both clocks are mach (s6967: G rows us= == mach*1e6).
  1. display grid: P 'at' values -> integer vsync index (running), least-squares period Td and phase; residual jitter
     (positive control: residual p99 < 0.5 ms means 'at' really is a vsync grid).
  2. VI grid: TL code 1 -> period Tv over the RT-on part (after --from).
  3. phase of every VI edge and every Q against the display grid, per 10 s bin, and the drift rate (ppm = (Tv-Td)/Td).
  4. level onsets (acq > --thr for >= --minrun presents after >= 10 low, as g1e_level_onset.py): phase of the onset Q vs the
     phase distribution of all Q; dq evenness; dp (P->P) of the onset and gpu_ms (H-compositor: dp 33 with even dq;
     H-gpu-late: gpu spike).
usage: g1e_vi_display_phase.py tl.bin.<pid> ring.txt [--from 95] [--thr 5] [--minrun 8]"""
import sys, struct, argparse, statistics as st, bisect, collections
ap = argparse.ArgumentParser(); ap.add_argument('tl'); ap.add_argument('ring'); ap.add_argument('--from', dest='frm', type=float, default=95)
ap.add_argument('--thr', type=float, default=5); ap.add_argument('--minrun', type=int, default=8); a = ap.parse_args()
pc = lambda v, p: sorted(v)[int(p * (len(v) - 1))] if v else float('nan')
raw = open(a.tl, 'rb').read(); n = len(raw) // 24
ev = sorted(struct.unpack_from('<qIIii', raw, i * 24) for i in range(n)); ev = [e for e in ev if e[0]]
vi = [(e[0] / 1e6, e[2]) for e in ev if e[1] == 1]
flips = [(e[0] / 1e6, e[2]) for e in ev if e[1] == 16]
t_first = vi[0][0]; tf = t_first + a.frm
Q = []; P = {}
for l in open(a.ring, errors='replace'):
    p = l.split()
    if len(p) < 2 or not l.endswith('\n'): continue
    kv = dict(x.split('=', 1) for x in p[2:] if '=' in x)
    try:
        if p[0] == 'Q' and kv.get('skip') == '0' and 'acq_ms' in kv:
            Q.append(dict(t=float(p[1]), acq=float(kv['acq_ms']), tp=float(kv['tp_ms']), gpu=float(kv['gpu_ms']), m=int(kv['mtl'])))
        elif p[0] == 'P' and float(kv.get('at', 0)) > 0: P[int(kv['mtl'])] = float(kv['at'])
    except (KeyError, ValueError): pass
Q.sort(key=lambda q: q['t']); Q = [q for q in Q if q['t'] >= tf]
def fit(ts, T0=1 / 60):
    ts = sorted(set(round(t, 7) for t in ts)); k = [0]
    for i in range(1, len(ts)): k.append(k[-1] + max(1, round((ts[i] - ts[i - 1]) / T0)))
    for _ in range(2):
        mk = st.mean(k); mt = st.mean(ts)
        b = sum((x - mk) * (y - mt) for x, y in zip(k, ts)) / sum((x - mk) ** 2 for x in k); a0 = mt - b * mk
        k = [0]
        for i in range(1, len(ts)): k.append(k[-1] + max(1, round((ts[i] - ts[i - 1]) / b)))
    res = [(y - (a0 + b * x)) * 1e3 for x, y in zip(k, ts)]
    return a0, b, res, ts, k
pa = [t for t in P.values() if t >= tf]
if len(pa) < 100: sys.exit('too few presented times (control failed)')
ad, Td, rd, pts, pk = fit(pa)
print(f'{a.ring}: {len(pa)} presented times after {a.frm:.0f}s; display Td={Td*1e3:.6f} ms ({1/Td:.5f} Hz), '
      f'ppm vs 60Hz {(Td*60-1)*1e6:+.1f}; residual p1/p50/p99 {pc(rd,.01):+.3f}/{pc(rd,.5):+.3f}/{pc(rd,.99):+.3f} ms '
      f'(control: |p99| < 0.5 means a vsync grid)')
# residual drift in halves: a non-constant display period shows as a residual trend
h = len(rd) // 2
print(f'  display residual median first half {st.median(rd[:h]):+.3f} ms, second half {st.median(rd[h:]):+.3f} ms')
vv = [t for t, k in vi if t >= tf]
av, Tv, rv, _, _ = fit(vv)
print(f'  VI Tv={Tv*1e3:.6f} ms, residual p1/p99 {pc(rv,.01):+.3f}/{pc(rv,.99):+.3f} ms; drift (Tv-Td)/Td = {(Tv/Td-1)*1e6:+.1f} ppm '
      f'-> full phase cycle every {abs(Td/(Tv/Td-1)) if Tv != Td else float("inf"):.0f} s; flips {[(round(t-t_first,1),s) for t,s in flips]}')
ph = lambda t: ((t - ad) / Td % 1.0) * Td * 1e3   # ms after the preceding display vsync
print('  bin(s) | VI phase p50 (spread p10..p90) | Q->next vsync p50 | acq p50 p90 | n')
B = collections.defaultdict(list)
for t in vv: B[int((t - t_first) // 10)].append(('v', ph(t)))
for q in Q: B[int((q['t'] - t_first) // 10)].append(('q', q))
for b in sorted(B):
    v = [x for k, x in B[b] if k == 'v']; qq = [x for k, x in B[b] if k == 'q']
    if not v or not qq: continue
    nx = [Td * 1e3 - ph(q['t']) for q in qq]; ac = [q['acq'] for q in qq]
    print(f'  {b*10:5d}  | {pc(v,.5):6.2f} ({pc(v,.1):5.2f}..{pc(v,.9):5.2f}) | {pc(nx,.5):6.2f} | {pc(ac,.5):5.2f} {pc(ac,.9):5.2f} | {len(qq)}')
hi = [q['acq'] > a.thr for q in Q]; nQ = len(Q); ons = []
for i in range(10, nQ):
    if hi[i] and not any(hi[i - 10:i]):
        j = i
        while j < nQ and hi[j]: j += 1
        if j - i >= a.minrun: ons.append(i)
allnx = [Td * 1e3 - ph(q['t']) for q in Q]
print(f'  onsets {len(ons)} (thr {a.thr}, minrun {a.minrun}); all-Q time-to-next-vsync p10/p50/p90 {pc(allnx,.1):.2f}/{pc(allnx,.5):.2f}/{pc(allnx,.9):.2f}')
for i in ons:
    q = Q[i]; dq = [(Q[j + 1]['t'] - Q[j]['t']) * 1e3 for j in range(i - 3, i)]
    dp = [(P.get(Q[j + 1]['m'], 0) - P.get(Q[j]['m'], 0)) * 1e3 for j in range(i - 3, i + 1)]
    vph = [ph(t) for t in vv if q['t'] - 0.6 < t <= q['t']]
    print(f'   t={q["t"]-t_first:6.1f} Q->next vsync {Td*1e3-ph(q["t"]):5.2f} ms  VI phase (last 0.6 s) {min(vph) if vph else float("nan"):5.2f}..{max(vph) if vph else float("nan"):5.2f}'
          f'  dq {" ".join(f"{x:4.1f}" for x in dq)}  dp {" ".join(f"{x:4.1f}" for x in dp)}  gpu {max(Q[j]["gpu"] for j in range(i-3,i+1)):.2f}'
          f'  acq pre {" ".join(f"{Q[j]["acq"]:.1f}" for j in range(i-3,i+1))}')
