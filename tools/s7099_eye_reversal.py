#!/usr/bin/env python3
"""s7099: per arbiter state (lim 1 = 60 fps, 2 = 30), how often the camera eye (0x80130C10) reverses direction between consecutive
game ticks while the craft keeps moving. rev = fraction of tick triples whose step vectors have a negative dot product
(a smooth follow camera gives ~0; an oscillating push-out gives a large value). Also reports the eye/player scale.
usage: s7099_eye_reversal.py game.log [t_from_s t_to_s]  (t = g3c t= field)"""
import re, math, sys
rx = re.compile(r'\[g3c\] vi=(\d+) t=([\d.]+) tasks=(\d+) lim=(\d+) m=(\d+) eye=([-\d.e+]+),([-\d.e+]+),([-\d.e+]+) cam=\S+ pl=([-\d.e+]+),([-\d.e+]+),([-\d.e+]+)')
lo = float(sys.argv[2]) if len(sys.argv) > 2 else 0; hi = float(sys.argv[3]) if len(sys.argv) > 3 else 1e9
R = []
for l in open(sys.argv[1], errors='replace'):
    g = rx.search(l)
    if g and lo <= float(g.group(2)) <= hi: R.append((int(g.group(4)), [float(g.group(k)) for k in (6, 7, 8)], [float(g.group(k)) for k in (9, 10, 11)]))
T = []  # new ticks: (lim, eye, pl)
for i in range(1, len(R)):
    if R[i][1] != R[i - 1][1]: T.append(R[i])
st = {}
for i in range(2, len(T)):
    if not (T[i][0] == T[i - 1][0] == T[i - 2][0]): continue
    a = [T[i - 1][1][k] - T[i - 2][1][k] for k in range(3)]; b = [T[i][1][k] - T[i - 1][1][k] for k in range(3)]
    pa = math.dist(T[i - 1][2], T[i - 2][2]); pb = math.dist(T[i][2], T[i - 1][2])
    if pa < 1e-3 or pb < 1e-3 or pa > 50: continue  # craft must be moving
    s = st.setdefault(T[i][0], [0, 0, 0.0, 0.0])
    s[1] += 1; s[0] += sum(a[k] * b[k] for k in range(3)) < 0; s[2] += math.sqrt(sum(v * v for v in b)); s[3] += pb
for k in sorted(st):
    s = st[k]; print('lim=%d triples %d rev %.3f eye-step/pl-step %.3f' % (k, s[1], s[0] / s[1], s[2] / s[3]))
