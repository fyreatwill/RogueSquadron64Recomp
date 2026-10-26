#!/usr/bin/env python3
"""s6320: find smoothly-moving, monotone float triples across RDRAM snapshots (pure python, no numpy).
Usage: g3c_ramscan.py SNAPDIR [skip_first=5]. Words with finite |v|<1e5, changing in >=60% of pairs, mostly one-signed steps,
no step >50% of range; reports aligned triples ranked by travel."""
import sys, glob, array, math
d = sys.argv[1]; skip = int(sys.argv[2]) if len(sys.argv) > 2 else 5
fs = sorted(glob.glob(d + '/snap_*.bin'))[skip:]
A = []
for f in fs:
    a = array.array('f'); a.frombytes(open(f, 'rb').read()); A.append(a)
n = len(A); N = len(A[0]); print(n, 'snapshots', N, 'words')
first, last = A[0], A[-1]
cand = {}
for w in range(N):
    x0, x1 = first[w], last[w]
    if not (abs(x0) < 1e5 and abs(x1) < 1e5) or abs(x1 - x0) < 1.0: continue   # nan fails compare
    v = [A[i][w] for i in range(n)]
    if not all(abs(t) < 1e5 for t in v): continue
    st = [v[i+1] - v[i] for i in range(n - 1)]
    rng = max(v) - min(v)
    if sum(1 for s in st if abs(s) > 1e-3) < 0.6 * len(st) or max(abs(s) for s in st) > 0.5 * rng: continue
    pos = sum(1 for s in st if s > 0); neg = sum(1 for s in st if s < 0)
    if max(pos, neg) < 0.7 * len(st): continue
    cand[w] = (rng, v)
print('candidate words', len(cand))
out = sorted(((cand[w][0] + cand[w+1][0] + cand[w+2][0], w) for w in cand if w+1 in cand and w+2 in cand), reverse=True)
for r, w in out[:25]:
    print('addr 0x%08X travel x%.1f y%.1f z%.1f first=%s' % (0x80000000 + 4*w, cand[w][0], cand[w+1][0], cand[w+2][0], [round(cand[w+k][1][0], 1) for k in range(3)]))
if not out:
    for w in list(cand)[:30]: print('word 0x%08X rng %.1f' % (0x80000000 + 4*w, cand[w][0]))
