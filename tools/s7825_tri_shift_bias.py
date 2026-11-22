#!/usr/bin/env python3
"""s7825: is a retail-vs-port quarter-pixel triangle residual systematic (scale/input) or sign-random (rounding noise)?

usage: python3 tools/s7825_tri_shift_bias.py RETAIL.bin PORT.bin --win r0:r1 --off o0:o1 [--controls]
  RETAIL/PORT: rdplog captures (raw or .zst, via rs64_zopen), as for tools/s7821_rdp_screen_segments.py --tri-geom.
  For each retail frame in r0:r1 the port frame at the best offset in o0:o1 is paired; every missed retail tri is matched to
  its nearest port tri, and each differing X edge word (XL/XH/XM) is classed OUTWARD/INWARD by the sign of (port-retail)
  against (x - frame centroid). Also prints the flip rate per time bin (a relative/scale input error shrinks with the object).
  Symmetric rounding noise -> inward fraction ~0.5; a smaller port object -> >0.5; larger -> <0.5.
--controls: same-run planted controls on the RETAIL frames themselves (offset 0): A shifts one X word of 10% of tris one
  quarter-pixel toward the centroid (must read inward >= 0.95), B shifts with random sign (must read 0.40..0.60). rc 3 on FAIL.
"""
import sys, collections, importlib.util, statistics, random, os, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rs64_zopen
a = [x for x in sys.argv[1:]]
def opt(n, d=None):
    return a[a.index(n) + 1] if n in a else d
if len(a) < 2 or '--win' not in a:
    print(__doc__); sys.exit(2)
sys.argv.append('--tri-geom')
s = importlib.util.spec_from_file_location('seg', os.path.join(HERE, 's7821_rdp_screen_segments.py'))
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
tmp = tempfile.mkdtemp(prefix='s7825_')
R = m.frames(rs64_zopen.materialize(a[0], tmp), True)
P = m.frames(rs64_zopen.materialize(a[1], tmp), False)
r0, r1 = map(int, opt('--win').split(':')); o0, o1 = map(int, opt('--off', '0:1').split(':'))
sx = lambda v: (v ^ 0x80000000) - 0x80000000
XF = (4, 6, 8)

def centroid(c):
    t = [sx(k[j]) / 65536 for k in c if k[0] == 'tri' for j in XF]
    return statistics.mean(t) if t else None

def score(R, P, r0, r1, o0, o1, tag):
    io = collections.Counter(); tb = collections.defaultdict(lambda: [0, 0, 0, 0]); nfr = 0
    for i in range(r0, r1):
        cands = [(sum(((R[i][0] - P[i + o][0]) + (P[i + o][0] - R[i][0])).values()), o) for o in range(o0, o1) if 0 <= i + o < len(P)]
        if not cands: continue
        q = P[i + min(cands)[1]][0]; cx = centroid(R[i][0])
        if cx is None: continue
        b_ = (i - r0) // 30; tb[b_][0] += 3 * sum(v for k, v in R[i][0].items() if k[0] == 'tri')
        rm = [t for t in (R[i][0] - q).elements() if t[0] == 'tri']; pm = [t for t in (q - R[i][0]).elements() if t[0] == 'tri']
        if rm: nfr += 1
        for t in rm:
            u = min(pm, key=lambda u: sum(x != y for x, y in zip(t[2:], u[2:])), default=None)
            if u is None: continue
            d = [j for j in range(2, len(t)) if t[j] != u[j]]
            for j in XF:
                if t[j] == u[j]: continue
                tb[b_][1] += 1
                if not set(d) <= set(XF): continue
                x = sx(t[j]) / 65536 - cx
                if abs(x) < 4: continue
                k = 'out' if (sx(u[j]) - sx(t[j]) > 0) == (x > 0) else 'in'
                io[k] += 1; tb[b_][2 if k == 'out' else 3] += 1
    n = io['in'] + io['out']; f = io['in'] / n if n else float('nan')
    print(f'{tag}: frames-with-miss {nfr}  pure-X words: inward {io["in"]} outward {io["out"]}  inward fraction {f:.3f}')
    return f, tb

def plant(R, r0, r1, mode, seed=7825):
    rnd = random.Random(seed); out = list(R)
    for i in range(r0, r1):
        c, mm = R[i]; cx = centroid(c); n = collections.Counter()
        for k, v in c.items():
            for _ in range(v):
                if k[0] == 'tri' and cx is not None and rnd.random() < 0.10:
                    j = rnd.choice(XF); x = sx(k[j]) / 65536 - cx
                    if abs(x) >= 4:
                        sg = (-1 if x > 0 else 1) if mode == 'in' else rnd.choice((-1, 1))
                        k2 = list(k); k2[j] = (k[j] + sg * 0x4000) & 0xFFFFFFFF; n[tuple(k2)] += 1; continue
                n[k] += 1
        out[i] = (n, mm)
    return out

f, tb = score(R, P, r0, r1, o0, o1, 'retail-vs-port')
print('time bin (30 frames): X words, flipped, out, in, flip rate')
for b_ in sorted(tb):
    t = tb[b_]; print(f'  {b_:3d} {t[0]:6d} {t[1]:6d} {t[2]:5d} {t[3]:5d} {t[1] / t[0] if t[0] else 0:.4f}')
rc = 0
if '--controls' in a:
    fa, _ = score(R, plant(R, r0, r1, 'in'), r0, r1, 0, 1, 'control A (planted inward)')
    fb, _ = score(R, plant(R, r0, r1, 'rand'), r0, r1, 0, 1, 'control B (planted random sign)')
    ok = fa >= 0.95 and 0.40 <= fb <= 0.60
    print('controls', 'PASS' if ok else 'FAIL'); rc = 0 if ok else 3
sys.exit(rc)
