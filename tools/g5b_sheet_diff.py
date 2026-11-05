#!/usr/bin/env python3
"""s6894 G5b: split ROGUESQ_G5B_SHEET triangles into visible (a g5b_drops event within the window) and quiet, then print
which state fields and triangle coefficient words differ.
usage: g5b_sheet_diff.py <sh.txt> <events.csv> [minT=0.04] [before_ms=60] [after_ms=10]"""
import sys, collections
minT = float(sys.argv[3]) if len(sys.argv) > 3 else 0.04
bef = float(sys.argv[4]) if len(sys.argv) > 4 else 60; aft = float(sys.argv[5]) if len(sys.argv) > 5 else 10
ev = [l.strip().split(',') for l in open(sys.argv[2])][1:]
ev = [int(e[6]) for e in ev if float(e[4]) >= minT]
rows = []
for l in open(sys.argv[1]):
    h, _, t = l.partition(' T ')
    p = h.split(); st = dict(x.split(':', 1) for x in p[5:]); w = [int(x, 16) for x in t.split()]
    rows.append(dict(sw=int(p[0]), t=int(p[1]), op=p[2][3:], area=float(p[3][5:]), h=p[4][2:], st=st, w=w))
print('sheets', len(rows), 'swaps', len({r['sw'] for r in rows}), 'events', len(ev))
def vis(r): return any(-aft < (r['t'] - m) / 24e3 + 0 < bef or -bef < (r['t'] - m) / 24e3 < aft for m in ev)
V = [r for r in rows if vis(r)]; Q = [r for r in rows if not vis(r)]
print('near events', len(V), 'quiet', len(Q))
for k in ['2D', '2F', '35', '38', '39', '3A', '3B', '3C', '3D', '3E', '3F']:
    cv = collections.Counter(r['st'].get(k) for r in V); cq = collections.Counter(r['st'].get(k) for r in Q)
    print(k, 'near', cv.most_common(4)); print(k, 'quiet', cq.most_common(4))
def row(r):
    w = r['w']; s = ''
    # tri layout: 8 edge words, then shade 64 B (op&4), tex 64 B (op&2), z 16 B (op&1)
    o = 8
    if int(r['op'], 16) & 4:
        s += ' RGBA %04X %04X %04X %04X' % (w[o] >> 16, w[o] & 0xFFFF, w[o+1] >> 16, w[o+1] & 0xFFFF); o += 16
    if int(r['op'], 16) & 2:
        s += ' STW %04X %04X %04X dsdx %08X dsdy %08X' % (w[o] >> 16, w[o] & 0xFFFF, w[o+1] >> 16, w[o+2], w[o+6]); o += 16
    if int(r['op'], 16) & 1: s += ' Z %08X dzdx %08X dzdy %08X' % (w[o], w[o+1], w[o+3])
    return s
print('--- near event'); [print(r['sw'], r['op'], int(r['area']), r['st']['3D'][-8:], 'h', r['h'], 'CC', r['st']['3C'], row(r)) for r in V[:24]]
print('--- quiet sample'); [print(r['sw'], r['op'], int(r['area']), r['st']['3D'][-8:], 'h', r['h'], 'CC', r['st']['3C'], row(r)) for r in Q[::max(1, len(Q)//16)]]
