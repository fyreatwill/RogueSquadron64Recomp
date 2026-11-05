#!/usr/bin/env python3
"""s6894 G5b: contact sheet of the presented frames (g5b_capture raw) nearest each mach time, 3 per row.
usage: g5b_frame_at.py <raw> <out.png> <mach> [mach...]   frames are taken 25 ms after the given swap time."""
import sys, struct, zlib, bisect
raw, out, ms = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3:]]
f = open(raw, 'rb'); t, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w*h*3
import os; n = os.path.getsize(raw)//rec; T = []
for i in range(n): f.seek(i*rec); T.append(struct.unpack('<Q', f.read(8))[0])
def fr(m):
    i = min(bisect.bisect_left(T, m + 600000), n-1); f.seek(i*rec+16); return f.read(w*h*3)
cols = 3; rows = []; F = [fr(m) for m in ms]
while len(F) % cols: F.append(bytes(w*h*3))
for r in range(0, len(F), cols):
    for y in range(h): rows.append(b''.join(F[r+c][y*w*3:(y+1)*w*3] + b'\xff\0\0'*3 for c in range(cols)))
    rows += [b'\xff\xff\0'*((w+3)*cols)]*3
W = (w+3)*cols
def ch(t, b): return struct.pack('>I', len(b)) + t + b + struct.pack('>I', zlib.crc32(t+b))
open(out, 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', W, len(rows), 8, 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(b''.join(b'\0'+r for r in rows), 6)) + ch(b'IEND', b''))
