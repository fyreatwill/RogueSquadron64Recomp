#!/usr/bin/env python3
"""Extract a 320x240 RGBA5551 framebuffer from a host-layout RDRAM dump to PPM and print mean RGB per 8x8 grid.
Usage: fb_from_rdram.py rdram.bin phys_addr out.ppm [width=320] [height=240]"""
import sys
d = bytearray(open(sys.argv[1], 'rb').read())
addr = int(sys.argv[2], 0) & 0x7FFFFF
w = int(sys.argv[4]) if len(sys.argv) > 4 else 320
h = int(sys.argv[5]) if len(sys.argv) > 5 else 240
import os
MODE = int(os.environ.get('FBMODE', '0'))  # 0 full word reverse, 1 raw, 2 swap halfwords
n = w * h * 2
seg = bytearray(d[addr:addr + n])
for i in range(0, n, 4):
    seg[i:i+4] = seg[i:i+4][::-1] if MODE == 0 else (seg[i:i+4] if MODE == 1 else seg[i+2:i+4] + seg[i:i+2])
out = bytearray()
grid = [[[0, 0, 0, 0] for _ in range(8)] for _ in range(8)]
for y in range(h):
    for x in range(w):
        v = (seg[(y*w+x)*2] << 8) | seg[(y*w+x)*2+1]
        r = ((v >> 11) & 31) * 255 // 31; g = ((v >> 6) & 31) * 255 // 31; b = ((v >> 1) & 31) * 255 // 31
        out += bytes((r, g, b))
        c = grid[y*8//h][x*8//w]; c[0] += r; c[1] += g; c[2] += b; c[3] += 1
open(sys.argv[3], 'wb').write(b'P6\n%d %d\n255\n' % (w, h) + out)
for row in grid:
    print(' '.join('%3d,%3d,%3d' % tuple(c[k]//c[3] for k in range(3)) for c in row))
