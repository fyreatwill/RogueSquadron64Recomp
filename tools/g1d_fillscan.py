#!/usr/bin/env python3
"""s6848: tabulate every RDP fill rect (0x36) in a port RDP bin by (colour-image addr, width, ul, lr); flag zero-width
fills (lr.x field 0 with ul.x 0) = the emitColorFillRect `(W & 0x3FF) << 14` wrap at W=1024.  usage: fillscan.py bin"""
import struct, sys, collections
data = open(sys.argv[1], 'rb').read(); o = 0
tab = collections.Counter(); first = {}; ci = (0, 0); fillc = 0; nrec = 0; vis = set()
while o + 16 <= len(data):
    mg, x, ln, vi = struct.unpack_from('<4I', data, o); o += 16; b = data[o:o + ln]; o += ln; nrec += 1; vis.add(vi)
    a = 0
    while a + 8 <= len(b):
        w0, w1 = struct.unpack_from('<II', b, a); op = (w0 >> 24) & 0x3F; n = 8
        if 0x08 <= op <= 0x0F: n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
        elif op in (0x24, 0x25): n = 16
        elif op == 0x3F: ci = (w1 & 0xFFFFFF, (w0 & 0x3FF) + 1)
        elif op == 0x37: fillc = w1
        elif op == 0x36:
            k = (ci[0], ci[1], (w1 >> 12) & 0xFFF, w1 & 0xFFF, (w0 >> 12) & 0xFFF, w0 & 0xFFF, fillc)
            tab[k] += 1; first.setdefault(k, vi)
        a += n
print('records', nrec, 'vi range', min(vis), max(vis))
print('   count  firstVI  ci_addr  cw   ul.x  ul.y  lr.x  lr.y  fillc  flag')
for k, c in sorted(tab.items(), key=lambda kv: -kv[1])[:100000]:
    flag = 'ZERO-W' if k[4] == 0 and k[2] == 0 and k[5] > k[3] else ''
    print('%8d %8d  %06X %4d %6.2f %5.2f %7.2f %6.2f %08X %s' % (c, first[k], k[0], k[1], k[2]/4, k[3]/4, k[4]/4, k[5]/4, k[6], flag))
