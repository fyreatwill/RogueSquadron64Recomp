#!/usr/bin/env python3
"""s7151: same-window dual-capture colour-space check. Pairs frames of two g5b_capture raws by displayTime (exact, else
nearest within 2 ms), and per pair reports mean |d| per channel for: srgb vs native (identity), srgb vs P3->sRGB(native)
(the s7150 FID_P3 transform, system Display P3.icc). H-src: second << first. H-partial: first ~ 0.
Positive control: --shift 30 mis-pairs by 30 frames (must raise both numbers on moving content).
usage: s7151_cs_compare.py srgb.raw nat.raw [--every N] [--shift K]"""
import sys, os, struct, bisect
from PIL import Image, ImageChops, ImageStat, ImageCms
class Raw:
    def __init__(s, p):
        s.f = open(p, 'rb'); _, s.w, s.h = struct.unpack('<QII', s.f.read(16)); s.rec = 16 + s.w*s.h*3
        s.T = []
        for i in range(os.path.getsize(p)//s.rec): s.f.seek(i*s.rec); s.T.append(struct.unpack('<Q', s.f.read(8))[0])
    def img(s, i): s.f.seek(i*s.rec+16); return Image.frombytes('RGB', (s.w, s.h), s.f.read(s.w*s.h*3))
a = sys.argv; A, B = Raw(a[1]), Raw(a[2])
every = int(a[a.index('--every')+1]) if '--every' in a else 20
shift = int(a[a.index('--shift')+1]) if '--shift' in a else 0
X = ImageCms.buildTransform(ImageCms.getOpenProfile('/System/Library/ColorSync/Profiles/Display P3.icc'), ImageCms.createProfile('sRGB'), 'RGB', 'RGB', renderingIntent=1)
tick = 1e-3*24e6  # mach ticks are 24 MHz on Apple silicon (1 tick = 41.67 ns)
rows = []
for i in range(0, len(A.T), every):
    j = bisect.bisect_left(B.T, A.T[i]); c = [k for k in (j-1, j) if 0 <= k < len(B.T)]
    if not c: continue
    j = min(c, key=lambda k: abs(B.T[k]-A.T[i]))
    if abs(B.T[j]-A.T[i]) > 2*tick: continue
    j += shift
    if not 0 <= j < len(B.T): continue
    s, n = A.img(i), B.img(j); cn = ImageCms.applyTransform(n, X)
    d0 = ImageStat.Stat(ImageChops.difference(s, n)).mean; d1 = ImageStat.Stat(ImageChops.difference(s, cn)).mean
    br = ImageStat.Stat(s).mean
    rows.append((i, j, d0, d1, br))
print(f"frames srgb {len(A.T)} nat {len(B.T)} paired {len(rows)} (every {every}, shift {shift})")
if rows:
    def m(k, c): return sum(r[k][c] for r in rows)/len(rows)
    print("identity srgb-nat     |d| R %.2f G %.2f B %.2f" % (m(2,0), m(2,1), m(2,2)))
    print("srgb - P3toSRGB(nat)  |d| R %.2f G %.2f B %.2f" % (m(3,0), m(3,1), m(3,2)))
    print("mean brightness srgb  R %.1f G %.1f B %.1f" % (m(4,0), m(4,1), m(4,2)))
    for r in rows[::max(1, len(rows)//8)]: print("  i %5d j %5d id %s conv %s" % (r[0], r[1], ' '.join('%.2f'%v for v in r[2]), ' '.join('%.2f'%v for v in r[3])))
