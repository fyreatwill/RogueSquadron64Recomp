#!/usr/bin/env python3
"""s7869: classify a non-exact island of a det-pair render comparison (tools/s7868_det_frame_cmp.py).

For each port frame j in [J0, J1) paired with retail j+OFF, report how many tris differ from retail and the PRIM values of
the differing tris, for the pinned arm P1 and the unpinned arm P2 (paired at its own offset OFF2). If P1 and P2 differ from
retail by DIFFERENT values on the same retail frames, the island is state-driven (the unpinned pre-tick-0 window), not a
fixed render defect (H-render would give the same wrong tris in both arms, since both run the same RSP/DL code).
Also prints the port phase ordinal / retail VI width of the island and of mission tick 0 (first frame of the next phase).
Control (iron rule 1): the island frames of P1 compared with themselves must give 0 differing tris, and a planted YH+1 on
one P1 tri must give exactly 1 port-only tri on that frame (rc 3 otherwise).
usage: s7869_island_probe.py RETAIL.bin P1.bin P2.bin OFF OFF2 J0 J1
"""
import sys, os, collections, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
a = sys.argv[1:]
if len(a) != 7: print(__doc__); sys.exit(2)
sys.argv.append('--tri-geom')
sp = importlib.util.spec_from_file_location('seg', os.path.join(HERE, 's7821_rdp_screen_segments.py'))
m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
R = m.frames(a[0], True); P1 = m.frames(a[1], False); P2 = m.frames(a[2], False)
off, off2, j0, j1 = map(int, a[3:])
C = lambda fr, i: collections.Counter(fr[i][0])
tri = lambda c: sum(v for k, v in c.items() if k[0] == 'tri')
same12 = 0; prims = collections.Counter(); n1 = n2 = 0; rows = []
for j in range(j0, j1):
    r = C(R, j + off); p1 = C(P1, j); jp2 = j + off - off2; p2 = C(P2, jp2) if 0 <= jp2 < len(P2) else collections.Counter()
    d1 = p1 - r; d2 = p2 - r
    n1 += tri(d1); n2 += tri(d2)
    for k in d1:
        if k[0] == 'tri': prims[k[1]] += d1[k]
    if d1 and d1 == d2: same12 += 1
    rows.append((j, j + off, tri(r), tri(d1), tri(d2), d1 == d2))
print(f'island port[{j0}:{j1}] retail[{j0 + off}:{j1 + off}] phase/width p1 {P1[j0][1]}..{P1[j1 - 1][1]} retail {R[j0 + off][1]}..{R[j1 - 1 + off][1]}')
print(f'next phase starts: port', next((i for i in range(j1, len(P1)) if P1[i][1] != P1[j1 - 1][1]), None),
      'retail', next((i for i in range(j1 + off, len(R)) if R[i][1] != R[j1 - 1 + off][1]), None))
print(f'p1 port-only tris {n1}, p2 port-only tris {n2}; frames where p1 diff == p2 diff (same wrong tris) {same12}/{j1 - j0}')
print('prim of differing p1 tris:', prims.most_common(8))
for row in rows[:3] + rows[-3:]: print('  port %d retail %d tris %d p1diff %d p2diff %d same %s' % row)
# controls
ok = sum(tri(C(P1, j) - C(P1, j)) for j in range(j0, j1)) == 0
c = C(P1, j0); k = next(k for k in c if k[0] == 'tri'); g = list(k); g[3] = (g[3] & ~0x3FFF) | ((g[3] + 1) & 0x3FFF)
c2 = c.copy(); c2[k] -= 1; c2[tuple(g)] += 1; c2 += collections.Counter()
ok = ok and tri(c2 - c) == 1
print('control (self 0, plant 1):', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 3)
