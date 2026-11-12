#!/usr/bin/env python3
"""s7207: H-motion vs H-shimmer on a capture span (PIL only). For consecutive delivered frames: mean abs diff d1(n,n+1), d2(n,n+2),
best vertical shift dy in -2..2 for n -> n+1, and the changed-pixel bbox (>8). Field bob/alternation gives d2 << d1 and a +-1 row
shift that cancels d1; motion gives d2 >= d1.   usage: s7207_motion.py ARM.raw t0 t1 ringfile"""
import struct, sys, statistics as st
from PIL import Image, ImageChops, ImageStat
raw, a, b, ring = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
t0 = float(next(l for l in open(ring) if l.startswith('Q ')).split()[1])
f = open(raw, 'rb'); _, w, h = struct.unpack('<QII', f.read(16)); f.seek(0); fs = w*h*3; F = []
while True:
    hd = f.read(16); d = f.read(fs)
    if len(d) < fs: break
    t = struct.unpack('<Q', hd[:8])[0]/24e6 - t0
    if a <= t <= b: F.append(Image.frombytes('RGB', (w, h), d).convert('L'))
D = lambda x, y: ImageStat.Stat(ImageChops.difference(x, y)).mean[0]
def sh(x, dy): return ImageChops.offset(x, 0, dy).crop((0, 3, w, h-3))
d1 = []; d2 = []; S = {}; bbs = []
for i in range(len(F)-2):
    x, y, z = F[i], F[i+1], F[i+2]; d1.append(D(x, y)); d2.append(D(x, z))
    yc = y.crop((0, 3, w, h-3)); k = min(range(-2, 3), key=lambda dy: D(sh(x, dy), yc)); S[k] = S.get(k, 0)+1
    bb = ImageChops.difference(x, y).point(lambda v: 255 if v > 8 else 0).getbbox()
    if bb: bbs.append(bb)
U = (min(q[0] for q in bbs), min(q[1] for q in bbs), max(q[2] for q in bbs), max(q[3] for q in bbs)) if bbs else None
print(f'{raw.split("/")[-1]} t{a}-{b}: n={len(F)} d1 med {st.median(d1):.3f} max {max(d1):.3f}  d2 med {st.median(d2):.3f}  bestshift {S}  pairs-with->8px {len(bbs)}  bbox-union {U}')
