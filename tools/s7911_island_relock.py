#!/usr/bin/env python3
"""s7911 G3: exact re-lock lag of a det pair on each side of a pre-flight island (load shift vs state island).

Every port frame (full tri-geom multiset, tools/s7821_rdp_screen_segments.frames) is hashed and looked up in ALL retail
frames; the retail-minus-port index lag of every exact match is voted, separately for the 160 frames before the island
[LO-160,LO), the island [LO,HI) and the 160 frames after [HI,HI+160).
Reading: H-loadshift (s7910, content re-keyed on elapsed time since a load whose stall differs) = post lag != pre lag
(m11 island B: pre 71 160/160, post 99 157/160 = 71 + 57/2). State island = post lag == pre lag (the scene re-converges on
the same frame alignment, so no frame-count / stall difference is involved: m6 island B pre 532 160/160, post 532 160/160).
Control (iron rule 1, same run): the pre window must lock >= 90% of its frames on one lag, rc 3 otherwise.
usage: s7911_island_relock.py RETAIL.bin[.zst] PORT.bin[.zst] LO HI
"""
import sys, os, importlib.util, tempfile, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import rs64_zopen
if len(sys.argv) != 5: print(__doc__); sys.exit(2)
R0, P0, lo, hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]); sys.argv = [sys.argv[0], '--tri-geom']
sp = importlib.util.spec_from_file_location('seg', os.path.join(HERE, 's7821_rdp_screen_segments.py'))
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
t = tempfile.mkdtemp(prefix='s7911r_')
h = lambda c: hash(frozenset(c.items()))
R = [h(c) for c, _ in m.frames(rs64_zopen.materialize(R0, t), True)]
P = [h(c) for c, _ in m.frames(rs64_zopen.materialize(P0, t), False)]
idx = collections.defaultdict(list)
for i, x in enumerate(R): idx[x].append(i)


def votes(a, b):
    v = collections.Counter(); n = 0
    for j in range(max(a, 0), min(b, len(P))):
        if idx.get(P[j]): n += 1; v.update(j - i for i in idx[P[j]])
    return n, v.most_common(3)


pre, isl, post = votes(lo - 160, lo), votes(lo, hi), votes(hi, hi + 160)
print(f'pre  [{lo - 160},{lo}): matched {pre[0]}/160 lags {pre[1]}')
print(f'isl  [{lo},{hi}): matched {isl[0]}/{hi - lo} lags {isl[1]}')
print(f'post [{hi},{hi + 160}): matched {post[0]}/160 lags {post[1]}')
ok = bool(pre[1]) and pre[1][0][1] >= 144
if ok and post[1]:
    d = post[1][0][0] - pre[1][0][0]
    print('verdict:', 'H-loadshift (lag moved %+d)' % d if d else 'state island (same lag both sides)')
print('control:', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 3)
