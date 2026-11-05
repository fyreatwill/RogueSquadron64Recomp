#!/usr/bin/env python3
"""s6894 G5b: join g5b_drops events to the ROGUESQ_G5B_TRIS stream. Per event prints, for swaps near the frame, tri count,
summed area, and the textures whose summed area jumps vs the median of neighbouring swaps.
usage: g5b_tri_join.py <tris.bin> <events.csv> [minT=0.04] [before_ms=170] [after_ms=30]"""
import sys, struct, mmap, collections, statistics
f = open(sys.argv[1], 'rb'); d = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
minT = float(sys.argv[3]) if len(sys.argv) > 3 else 0.04
bef = float(sys.argv[4]) if len(sys.argv) > 4 else 170; aft = float(sys.argv[5]) if len(sys.argv) > 5 else 30
M = b'\xf5\xf5\xf5\xf5'; sw = []; p = d.find(M)
while p >= 0:
    t, q = struct.unpack_from('<QI', d, p + 4); sw.append((p, t, q)); p = d.find(M, p + 16)
sw = [s for i, s in enumerate(sw) if i == 0 or (s[0] - sw[i-1][0] - 16) % 32 == 0]
def stats(i):
    a = sw[i][0] + 16; b = sw[i + 1][0] if i + 1 < len(sw) else len(d); out = collections.Counter(); cnt = collections.Counter()
    for o in range(a, b, 32):
        op, _, cw, timg, z = struct.unpack_from('<BBHII', d, o); c = struct.unpack_from('<10h', d, o + 12)
        ar = 0
        for k in range(5):
            x0, y0, x1, y1 = c[2*k], c[2*k+1], c[(2*k+2) % 10], c[(2*k+3) % 10]; ar += x0 * y1 - x1 * y0
        ar = abs(ar) / 32; out[timg] += ar; cnt[timg] += 1
    return out, cnt
for l in list(open(sys.argv[2]))[1:]:
    e = l.strip().split(',')
    if float(e[4]) < minT: continue
    m = int(e[6]); idx = [i for i, s in enumerate(sw) if -bef < (s[1] - m) / 24e3 < aft]
    if not idx: continue
    print('EVENT', e[0], 't', e[1], 'k', e[3], 'T', e[4])
    base = [stats(i) for i in range(max(0, idx[0] - 8), idx[0] - 2)]
    for i in idx:
        o, c = stats(i); r = []
        for t in set(o):
            med = statistics.median(b[0].get(t, 0) for b in base)
            r.append((o[t] - med, t, o[t], med, c[t]))
        r.sort(reverse=True)
        print('  %+5.0fms swap %d n=%d sum=%.0f' % ((sw[i][1] - m) / 24e3, sw[i][2], sum(c.values()), sum(o.values())), ' '.join('%08X:+%.0f(%d)' % (x[1], x[0], x[4]) for x in r[:3]), '| lost', ' '.join('%08X:%.0f' % (x[1], x[0]) for x in r[-2:]))
