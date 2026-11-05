#!/usr/bin/env python3
"""s6894 G5b: stdlib-only contact sheet from g5b_drops PPM triplets. Rows = events, columns = before / transient / after.
usage: g5b_sheet.py <out.png> <dumpdir> <idx> [idx...]   (host python has no PIL)"""
import sys, zlib, struct
def ppm(p):
    d = open(p, 'rb').read(); parts = d.split(b'\n', 3); w, h = map(int, parts[1].split()); return w, h, parts[3]
def png(path, w, h, rows):
    raw = b''.join(b'\0' + r for r in rows)
    def ch(t, b): return struct.pack('>I', len(b)) + t + b + struct.pack('>I', zlib.crc32(t + b))
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(raw, 6)) + ch(b'IEND', b''))
out, dd, ids = sys.argv[1], sys.argv[2], sys.argv[3:]
rows = []; W = 0
for i in ids:
    fr = [ppm(f'{dd}/{int(i):06d}_{s}.ppm') for s in 'axb']
    w, h = fr[0][:2]; W = 3 * w + 8
    for y in range(h):
        rows.append(fr[0][2][y*w*3:(y+1)*w*3] + b'\xff\0\0'*4 + fr[1][2][y*w*3:(y+1)*w*3] + b'\xff\0\0'*4 + fr[2][2][y*w*3:(y+1)*w*3])
    rows += [b'\xff\xff\0' * W] * 3
png(out, W, len(rows), rows)
