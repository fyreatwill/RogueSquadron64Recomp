#!/usr/bin/env python3
"""s6894 G5b: does the RDP actually draw a sheet? Walks scanlines with the RDP rule: lft=w0 bit 23; xmajor=H edge,
xminor=M then L. lft=1 draws xmajor..xminor rightward, lft=0 leftward; an inverted span draws nothing. Reports the real
drawn on-screen pixels inside the scissor against the hull area, per class.
usage: g5b_sheet_span.py <sh.txt> [events.csv] [minT=0.04]"""
import sys, collections
def s32(v): return v - (1 << 32) if v & 0x80000000 else v
fx = lambda v: s32(v) / 65536.0
sy = lambda v: ((v & 0x3FFF) ^ 0x2000) - 0x2000
ev = []
if len(sys.argv) > 2:
    mt = float(sys.argv[3]) if len(sys.argv) > 3 else 0.04
    ev = [int(l.split(',')[6]) for l in list(open(sys.argv[2]))[1:] if float(l.split(',')[4]) >= mt]
C = collections.Counter(); ex = []
for l in open(sys.argv[1]):
    h, _, t = l.partition(' T '); p = h.split(); w = [int(x, 16) for x in t.split()]
    st = dict(x.split(':', 1) for x in p[5:]); s0, s1 = [int(x, 16) for x in st['2D'].split(',')]
    X0, Y0, X1, Y1 = ((s0 >> 12) & 0xFFF) / 4, (s0 & 0xFFF) / 4, ((s1 >> 12) & 0xFFF) / 4, (s1 & 0xFFF) / 4
    lft = (w[0] >> 23) & 1; yl, ym, yh = sy(w[0]) / 4, sy(w[1] >> 16) / 4, sy(w[1]) / 4
    xl, dl, xh, dh, xm, dm = [fx(w[i]) for i in range(2, 8)]
    drawn = inv = 0; y = int(max(Y0, yh))
    while y < min(Y1, yl):
        a = xh + dh * (y - yh); b = (xm + dm * (y - yh)) if y < ym else (xl + dl * (y - ym))
        L, R = (a, b) if lft else (b, a)
        if R >= L: drawn += max(0, min(R, X1) - max(L, X0))
        else: inv += max(0, min(L, X1) - max(R, X0))
        y += 1
    tm = int(p[1]); near = any(-60 < (tm - m) / 24e3 < 10 for m in ev); area = float(p[3][5:])
    cls = 'draws' if drawn > 0.25 * (drawn + inv + 1) else 'inverted'
    C[(cls, near, p[2][3:])] += 1
    ex.append((int(p[0]), tm, p[2][3:], lft, int(area), int(drawn), int(inv), near, st['3D'][-8:]))
for k in sorted(C): print(k, C[k])
print('swap op lft hull drawn inverted near tex   (largest inverted)')
for r in sorted(ex, key=lambda r: -r[6])[:8]: print(r[0], *r[2:])
print('(largest drawn, op0F)')
for r in sorted([e for e in ex if e[2] == '0F'], key=lambda r: -r[5])[:8]: print(r[0], *r[2:])
