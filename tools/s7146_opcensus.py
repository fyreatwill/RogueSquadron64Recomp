#!/usr/bin/env python3
"""s7146: per-swap RDP op census of a G5B capture (tri/texrect/fill/cimg/scissor), to tell which draw path a scene uses.
usage: s7146_opcensus.py cap swap[,swap...]"""
import struct, sys, collections
cap = sys.argv[1]; want = set(map(int, sys.argv[2].split(','))); f = open(cap, 'rb'); cur = None; out = collections.defaultdict(collections.Counter)
while True:
    t = f.read(4)
    if len(t) < 4: break
    tag = struct.unpack('<I', t)[0]
    if tag == 0x50415753:
        _, cur = struct.unpack('<QI', f.read(12))
        if cur > max(want): break
        continue
    if tag == 0x204D4152: f.seek(0x1000000, 1); continue
    lo, n = struct.unpack('<II', f.read(8))
    if cur not in want: f.seek(n, 1); continue
    c = f.read(n); a = 0; C = out[cur]
    while a + 8 <= n:
        w0, w1 = struct.unpack('<II', c[a:a + 8]); op = (w0 >> 24) & 0x3F; l = 8
        if 8 <= op <= 15: l = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0); C['tri%02X' % op] += 1
        elif op in (0x24, 0x25):
            l = 16; C['texrect'] += 1
            xh, yh, xl, yl = ((w1 >> 12) & 0xFFF) / 4, (w1 & 0xFFF) / 4, ((w0 >> 12) & 0xFFF) / 4, (w0 & 0xFFF) / 4
            C['rx %d-%d' % (xh // 128 * 128, xl // 128 * 128)] += 1
        elif op == 0x36: C['fill %d,%d-%d,%d' % (((w1 >> 12) & 0xFFF) >> 2, (w1 & 0xFFF) >> 2, ((w0 >> 12) & 0xFFF) >> 2, (w0 & 0xFFF) >> 2)] += 1
        elif op == 0x3F: C['cimg w%d @%06X' % ((w0 & 0x3FF) + 1, w1 & 0xFFFFFF)] += 1
        elif op == 0x3D: C['timg w%d @%06X' % ((w0 & 0x3FF) + 1, w1 & 0xFFFFFF)] += 0; C['timg'] += 1
        elif op == 0x2D: C['sciss %d,%d-%d,%d' % (((w0 >> 12) & 0xFFF) >> 2, (w0 & 0xFFF) >> 2, ((w1 >> 12) & 0xFFF) >> 2, (w1 & 0xFFF) >> 2)] += 1
        a += l
for s in sorted(out): print(s, dict(out[s].most_common(14)))
