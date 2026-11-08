#!/usr/bin/env python3
"""s6968 G1e: same-run before/after for ROGUESQ_VI_LOCK_AT=<s> (VI grid servoed so RT64's workload submit W sits TARGET ms after the
display vsync). Per block (before = [--from, AT), after = [AT + --settle, end)):
  W phase p10/p50/p90 (ms after the display vsync; display grid fitted from P 'at' = presentedTime), lat p50 (P - Q + tp), acq p50 and
  share > 5 ms, misses/s (shown P->P >= 25 ms), drain drops (D rows), VI interval p1/p50/p99 and mean rate (TL code 1; audio is per VI,
  so the mean must stay 60.00).
Positive control: the after block's W phase p50 must sit within 1.5 ms of the target (the lock engaged) -- else the comparison is void.
usage: g1e_vi_lock_ab.py tl.bin.<pid> ring.txt [--at 130] [--from 95] [--settle 10] [--target 10]"""
import sys, struct, argparse, statistics as st
ap = argparse.ArgumentParser(); ap.add_argument('tl'); ap.add_argument('ring')
for k, v in (('at', 130), ('from', 95), ('settle', 10), ('target', 10)): ap.add_argument('--' + k, dest=k.replace('from', 'frm'), type=float, default=v)
a = ap.parse_args()
pc = lambda v, p: sorted(v)[int(p * (len(v) - 1))] if v else float('nan')
raw = open(a.tl, 'rb').read(); n = len(raw) // 24
ev = sorted(struct.unpack_from('<qIIii', raw, i * 24) for i in range(n)); vi = [e[0] / 1e6 for e in ev if e[0] and e[1] == 1]
t0 = vi[0]
W = []; Q = []; P = {}; D = []
for l in open(a.ring, errors='replace'):
    p = l.split()
    if len(p) < 2 or not l.endswith('\n'): continue
    kv = dict(x.split('=', 1) for x in p[2:] if '=' in x)
    try:
        t = float(p[1]) - t0
        if p[0] == 'W': W.append(t)
        elif p[0] == 'D': D.append(t)
        elif p[0] == 'Q' and kv.get('skip') == '0' and 'acq_ms' in kv: Q.append((t, float(kv['acq_ms']), kv['mtl'], float(kv['tp_ms'])))
        elif p[0] == 'P' and float(kv.get('at', 0)) > 0: P[kv['mtl']] = float(kv['at']) - t0
    except (KeyError, ValueError): pass
ps = sorted(v for v in P.values() if v > a.frm)
Td = 1 / 60; k = [0]
for i in range(1, len(ps)): k.append(k[-1] + max(1, round((ps[i] - ps[i - 1]) / Td)))
mk = st.mean(k); mt = st.mean(ps); Td = sum((x - mk) * (y - mt) for x, y in zip(k, ps)) / sum((x - mk) ** 2 for x in k); ref = mt - Td * mk
ph = lambda t: ((t - ref) / Td % 1) * Td * 1e3
end = max(ps)
def block(lo, hi):
    w = [ph(t) for t in W if lo <= t < hi]
    q = [x for x in Q if lo <= x[0] < hi and x[2] in P]
    lat = [(P[x[2]] - x[0]) * 1e3 + x[3] for x in q]; acq = [x[1] for x in q]
    shown = sorted(P[x[2]] for x in q); miss = sum(1 for u, v in zip(shown, shown[1:]) if v - u >= 0.025)
    v = [x for x in vi if lo + t0 <= x < hi + t0]; dv = [(y - x) * 1e3 for x, y in zip(v, v[1:])]
    dur = hi - lo
    return dict(w=w, lat=pc(lat, .5), acq=pc(acq, .5), a5=100 * sum(x > 5 for x in acq) / max(1, len(acq)), miss=miss / dur,
                drops=sum(lo <= t < hi for t in D), dv=dv, rate=(len(v) - 1) / ((v[-1] - v[0]) if len(v) > 1 else 1), dur=dur)
print(f'{a.ring}: display Td {Td*1e3:.5f} ms; target W phase {a.target} ms')
print('block  |   t0..t1   | W ph p10/p50/p90    | lat p50 | acq p50 >5% | miss/s | drops | VI dt p1/p50/p99   rate')
res = {}
for name, lo, hi in (('before', a.frm, a.at), ('after', a.at + a.settle, end)):
    b = block(lo, hi); res[name] = b
    print(f'{name:6s} | {lo:4.0f}..{hi:4.0f} | {pc(b["w"],.1):5.2f} {pc(b["w"],.5):5.2f} {pc(b["w"],.9):5.2f} | {b["lat"]:7.1f} | {b["acq"]:5.2f} {b["a5"]:5.1f} |'
          f' {b["miss"]:6.3f} | {b["drops"]:5d} | {pc(b["dv"],.01):5.2f} {pc(b["dv"],.5):5.2f} {pc(b["dv"],.99):5.2f} {b["rate"]:.3f}')
ok = abs(pc(res['after']['w'], .5) - a.target) < 1.5
print(f'control: after-block W p50 {pc(res["after"]["w"],.5):.2f} vs target {a.target} -> {"ENGAGED" if ok else "NOT ENGAGED (comparison void)"}')
