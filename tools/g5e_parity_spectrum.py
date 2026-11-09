#!/usr/bin/env python3
"""s7017: is the s7010 mach-parity split biased by a periodic load? Per 1 s mach bucket mean rsp/run/T (same frame
extraction as g5e_cost_by_parity.py), then autocorrelation lags 1..10 s, and the odd-even delta for each sub-second
offset of the bucket grid (0..900 ms). H-periodic: a ~2 s autocorrelation peak (lag2 > 0, lag1 < 0) and an odd-even
delta that follows a sinusoid over the offset grid. A drift: all lags positive and decaying. Noise: |lag k| ~ 1/sqrt(n).
Also a hashed per-second arm (splitmix32 of the second index) as the candidate de-biased split, same frames.
Usage: g5e_parity_spectrum.py <tl.bin.pid> <log-with-anchor> [--skip-s 130] [--key rsp]
"""
import struct, sys, argparse, re, collections, statistics as st
ap = argparse.ArgumentParser(); ap.add_argument('tl'); ap.add_argument('log')
ap.add_argument('--skip-s', type=float, default=130.0); ap.add_argument('--key', default='rsp')
a = ap.parse_args()
m = None
for ln in open(a.log, errors='replace'):
    mm = re.search(r'\[s7010-clk\] steady_us=(-?\d+) mach=(\d+)', ln)
    if mm: m = (int(mm.group(1)), int(mm.group(2))); break
if not m: sys.exit('no anchor')
S, M = m
raw = open(a.tl, 'rb').read(); n = len(raw) // 24
ev = sorted((r[0], r[1], r[2], r[4]) for r in (struct.unpack_from('<qIIii', raw, i * 24) for i in range(n)) if r[0] != 0)
t0 = ev[0][0]; ev = [e for e in ev if e[0] - t0 >= a.skip_s * 1e6]
G = collections.Counter(e[3] for e in ev if e[1] == 15).most_common(1)[0][0]
sw = [i for i, e in enumerate(ev) if e[1] == 15 and e[3] == G]
fr = []
for k in range(len(sw) - 1):
    a0, a1 = sw[k], sw[k + 1]; ta, tb = ev[a0][0], ev[a1][0]
    blk = 0.0; op = None; last6 = None; rsp = 0.0
    for x in range(a0, a1):
        e = ev[x]
        if e[3] == G:
            if e[1] == 10: op = e[0]
            elif e[1] == 11 and op is not None: blk += (e[0] - op) / 1e3; op = None
        if e[1] == 6: last6 = e[0]
        elif e[1] == 7 and last6 is not None: rsp += (e[0] - last6) / 1e3; last6 = None
    if op is not None: blk += (tb - op) / 1e3
    fr.append(dict(mach=M + (ta - S) * 24, T=(tb - ta) / 1e3, run=(tb - ta) / 1e3 - blk, rsp=rsp))
def h32(x):
    x = (x + 0x9E3779B9) & 0xFFFFFFFF; x ^= x >> 16; x = (x * 0x85EBCA6B) & 0xFFFFFFFF
    x ^= x >> 13; x = (x * 0xC2B2AE35) & 0xFFFFFFFF; x ^= x >> 16; return x
K = a.key
def buckets(off_ms):
    b = collections.defaultdict(list)
    for f in fr: b[int((f['mach'] - off_ms * 24000) // 24000000)].append(f[K])
    return {s: st.mean(v) for s, v in b.items() if len(v) >= 20}
b = buckets(0); secs = sorted(b); s0, s1 = secs[0], secs[-1]
xs = [b.get(s) for s in range(s0, s1 + 1)]
mu = st.mean(v for v in xs if v is not None); var = st.mean((v - mu) ** 2 for v in xs if v is not None)
print(f'frames={len(fr)} buckets={len(b)} mean {K}={mu:.2f} sd={var ** .5:.2f}  (noise ~ +-{2 / len(b) ** .5:.2f})')
ac = []
for L in range(1, 11):
    p = [(xs[i] - mu) * (xs[i + L] - mu) for i in range(len(xs) - L) if xs[i] is not None and xs[i + L] is not None]
    ac.append(st.mean(p) / var if p else float('nan'))
print(' autocorr lag1..10: ' + ' '.join(f'{v:+.2f}' for v in ac))
print(' odd-even delta by bucket offset (ms): ' + ' '.join(
    f'{o}:{(lambda bb: st.mean(v for s, v in bb.items() if s & 1) - st.mean(v for s, v in bb.items() if not s & 1))(buckets(o)):+.2f}'
    for o in range(0, 1000, 100)))
odd = [v for s, v in b.items() if h32(s) & 1]; ev_ = [v for s, v in b.items() if not h32(s) & 1]
print(f' hashed split (splitmix32(sec)&1): on n={len(odd)} off n={len(ev_)} delta {st.mean(odd) - st.mean(ev_):+.2f}')
# per-second odd/even with half the series each, to see if the sign is stable
h = len(secs) // 2
for nm, ss in (('first half', secs[:h]), ('second half', secs[h:])):
    o = [b[s] for s in ss if s & 1]; e = [b[s] for s in ss if not s & 1]
    print(f' {nm}: odd-even {st.mean(o) - st.mean(e):+.2f}')
