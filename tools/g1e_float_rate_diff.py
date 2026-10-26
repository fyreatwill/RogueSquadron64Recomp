#!/usr/bin/env python3
"""s6257: float-aware companion to g1e_rate_diff.py. For every rdram word read as host-native float32, per-real-second |delta| in
retail (30 fps) vs lever (60 fps) windows; a word whose position advances 2x per real second shows ratio ~2, delta-time motion ~1.
usage: g1e_float_rate_diff.py <run.log> [first_snap_n=6]. Pure python."""
import re, sys, array, math, statistics as st
log = sys.argv[1]; first = int(sys.argv[2]) if len(sys.argv) > 2 else 6
snaps = {int(m[1]): (m[2], m[3], float(m[4])) for m in re.finditer(r'\[g1e-snap\] n=(\d+) file=(\S+) tag=(\S+) sec=([\d.]+)', open(log, errors='replace').read())}
W = {'end-retail': [], 'end-lever': []}; prev = None
for i in sorted(snaps):
    f, tag, sec = snaps[i]
    a = array.array('f'); a.frombytes(open(f, 'rb').read())
    if prev is not None and tag in W and i >= first: W[tag].append([abs(x - y) / sec if (math.isfinite(x) and math.isfinite(y) and abs(x) < 1e5 and abs(y) < 1e5) else -1 for x, y in zip(a, prev)])
    prev = a
R, L = W['end-retail'], W['end-lever']; print({k: len(v) for k, v in W.items()})
if len(R) < 2 or len(L) < 2: sys.exit('need >=2 windows per arm')
hist = {}; ex = {}
for j in range(len(R[0])):
    r = [w[j] for w in R]; l = [w[j] for w in L]
    if min(r + l) < 0: continue
    mr, ml = st.median(r), st.median(l)
    if mr < 0.5 or mr > 5000: continue
    if st.pstdev(r) > mr * 0.4 or st.pstdev(l) > ml * 0.4 + 0.1: continue
    q = ml / mr; b = round(q * 4) / 4; hist[b] = hist.get(b, 0) + 1; ex.setdefault(b, []).append((0x80100000 + 4 * j, mr, ml))
print('ratio-bucket count'); [print(f'  {b:.2f} {n}') for b, n in sorted(hist.items())]
for b in sorted(ex):
    if 1.75 <= b <= 2.25:
        print('ratio~2 words:'); [print(f'  0x{a:08X} retail/s={mr:.2f} lever/s={ml:.2f}') for a, mr, ml in ex[b][:30]]
for a, mr, ml in ex.get(1.0, [])[:6]: print(f'  ctl~1: 0x{a:08X} {mr:.2f} {ml:.2f}')
