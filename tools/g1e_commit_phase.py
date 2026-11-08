#!/usr/bin/env python3
"""s6986 G1e: phase of each present-buffer commit (S row c) relative to the on-glass vsync grid (P row at), split by the
present's on-glass interval (late 30-40 ms vs normal 15-18.5 ms). Usage: g1e_commit_phase.py ring.txt [--from s]"""
import sys, bisect, collections
rf = sys.argv[1]; t_from = float(sys.argv[sys.argv.index('--from') + 1]) if '--from' in sys.argv else 95.0
S = {}; P = []
for l in open(rf, errors='replace'):
    p = l.split()
    if len(p) < 3 or not l.endswith('\n'): continue
    kv = dict(x.split('=', 1) for x in p[2:] if '=' in x)
    try:
        if p[0] == 'S': S[int(kv['mtl'])] = float(kv['c'])
        elif p[0] == 'P' and float(kv.get('at', 0)) > 0: P.append((float(kv['at']), int(kv['mtl'])))
    except (KeyError, ValueError): pass
P.sort(); at = [x[0] for x in P]; t0 = at[0]
iv = sorted(b - a for a, b in zip(at, at[1:]) if 0.0155 < b - a < 0.0178); per = iv[len(iv) // 2]
rows = {'late': [], 'norm': []}
for j in range(1, len(P)):
    d = (P[j][0] - P[j - 1][0]) * 1e3; m = P[j][1]
    if m not in S or P[j][0] - t0 < t_from: continue
    c = S[m]; k = bisect.bisect_right(at, c) - 1
    if k < 0: continue
    ph = ((c - at[k]) % per) * 1e3                 # ms after the last vsync that put a frame on glass
    lat = (P[j][0] - c) * 1e3; nv = round(lat / (per * 1e3))
    key = 'late' if 30 <= d < 40 else ('norm' if 15 < d < 18.5 else None)
    if key: rows[key].append((ph, lat, nv))
print(f'vsync period {per*1e3:.3f} ms; late {len(rows["late"])} normal {len(rows["norm"])}')
for nm, R in rows.items():
    if not R: continue
    h = collections.Counter(int(r[0] // 2) * 2 for r in R); nvc = collections.Counter(r[2] for r in R)
    print(f'  {nm:4s} commit phase hist (2 ms bins): ' + ' '.join(f'{b:02d}:{h[b]}' for b in range(0, 18, 2)))
    print(f'  {nm:4s} vsyncs commit->glass: ' + ' '.join(f'{k}:{v}' for k, v in sorted(nvc.items())))
