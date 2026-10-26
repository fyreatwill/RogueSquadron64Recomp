#!/usr/bin/env python3
"""s6256: compare per-real-second rates of every rdram word between retail (30 fps) and lever (60 fps) windows.
usage: g1e_rate_diff.py <run.log> [first_snap_n=6]; reads [g1e-snap] lines for file/sec/tag; snapshots cover 0x80100000..0x80300000.
Pure python (no numpy on this box)."""
import re, sys, array, statistics as st
log = sys.argv[1]; first = int(sys.argv[2]) if len(sys.argv) > 2 else 6
snaps = {int(m[1]): (m[2], m[3], float(m[4])) for m in re.finditer(r'\[g1e-snap\] n=(\d+) file=(\S+) tag=(\S+) sec=([\d.]+)', open(log, errors='replace').read())}
def load(f):
    a = array.array('I'); a.frombytes(open(f, 'rb').read())
    if sys.byteorder == 'little': a.byteswap()  # rdram words are big-endian-in-u32 as dumped natively; keep as dumped
    return a
raw = lambda f: (lambda a: a)(array.array('I', open(f, 'rb').read()))
W = {'end-retail': [], 'end-lever': []}
prev = None
for i in sorted(snaps):
    f, tag, sec = snaps[i]
    a = array.array('I'); a.frombytes(open(f, 'rb').read())
    if prev is not None and tag in W and i >= first:
        W[tag].append([(((x - y) + 2**31) % 2**32 - 2**31) / sec for x, y in zip(a, prev)])
    prev = a
print({k: len(v) for k, v in W.items()})
R, L = W['end-retail'], W['end-lever']
if len(R) < 2 or len(L) < 2: sys.exit('need >=2 windows per arm')
out = {'FRAME-LOCKED': [], 'TIME-BASED': [], 'HALVED': []}
for j in range(len(R[0])):
    r = [w[j] for w in R]; l = [w[j] for w in L]
    mr, ml = st.median(r), st.median(l)
    if abs(mr) < 5 or abs(mr) > 1e6: continue
    if st.pstdev(r) > abs(mr) * 0.3 or st.pstdev(l) > abs(ml) * 0.3 + 1: continue
    q = ml / mr
    k = 'FRAME-LOCKED' if 1.8 < q < 2.2 else 'TIME-BASED' if 0.9 < q < 1.1 else 'HALVED' if 0.4 < q < 0.6 else None
    if k: out[k].append((0x80100000 + 4 * j, mr, ml, q))
for k, v in out.items():
    print(f'== {k}: {len(v)} words')
    for a, mr, ml, q in v[:40]: print(f'  0x{a:08X} retail/s={mr:.2f} lever/s={ml:.2f} ratio={q:.2f}')
