#!/usr/bin/env python3
"""s7133: per-swap FillRect (op 0x36) list of a ROGUESQ_G5B_FRAME capture, tagged by the current colour image address.
usage: s7133_rects.py cap swap [swap ...]   (swaps ascending)"""
import struct, sys
cap = sys.argv[1]; want = sorted(map(int, sys.argv[2:])); f = open(cap, 'rb'); sw = -1; out = {}
while True:
    t = f.read(4)
    if len(t) < 4: break
    tag = struct.unpack('<I', t)[0]
    if tag == 0x50415753:
        _, sw = struct.unpack('<QI', f.read(12))
        if sw > want[-1]: break
        continue
    if tag == 0x204D4152: f.seek(0x1000000, 1); continue
    lo, n = struct.unpack('<II', f.read(8))
    if sw not in want: f.seek(n, 1); continue
    c = f.read(n); a = 0; ci = out.setdefault(sw, [None, []])
    rw = lambda o: struct.unpack('<I', c[o:o + 4])[0]
    while a + 8 <= n:
        w0 = rw(a); op = (w0 >> 24) & 0x3F; l = 8
        if 8 <= op <= 15: l = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
        elif op in (0x24, 0x25): l = 16
        if op == 0x3F: ci[0] = rw(a + 4) & 0xFFFFFF
        if op == 0x36:
            w1 = rw(a + 4); ci[1].append('%06X:{%d,%d,%d,%d}' % (ci[0] or 0, (w1 >> 14) & 0x3FF, (w1 >> 2) & 0x3FF, (w0 >> 14) & 0x3FF, (w0 >> 2) & 0x3FF))
        a += l
for s in want: print(s, ' '.join(out.get(s, [0, ['absent']])[1]))
