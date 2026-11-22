#!/usr/bin/env python3
"""s5913: min distance from the logged player track ([plpos]) to every distinct class-1 sphere centre ([sph] P ctr)
in a g1_fireall run.log.  usage: g1_track_vs_spheres.py run.log"""
import re, math, sys
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from rs64_zopen import zopen, zbytes  # s7805: zst-only retained inputs
P, S, C = [], [], set()
for l in zopen(sys.argv[1], errors='ignore'):
    if l.startswith('[plpos]'):
        m = re.search(r'pos=\(([-\d.]+),([-\d.]+),([-\d.]+)\)', l)
        if m: P.append(tuple(map(float, m.groups()))); S.append('sx=0.0 sy=0.0' not in l)
    m = re.match(r'\[sph\] P ctr=\(([-\d.]+),([-\d.]+),([-\d.]+)\) r2=([\d.e-]+)', l)
    if m: C.add(tuple(map(float, m.groups())))
print('plpos samples', len(P), 'nonzero-stick samples', sum(S))
for c in sorted(C):
    print(c[:3], 'r=%.2f' % math.sqrt(c[3]), 'min track dist %.1f' % min(math.dist(p, c[:3]) for p in P))
