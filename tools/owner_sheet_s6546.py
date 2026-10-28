#!/usr/bin/env python3
"""s6546 same-run pair sheet: frames straddling a CAP_ALT toggle (rev order: inf,120,0 per 60 swaps).
Usage: owner_sheet_s6546.py fbd_dir out.png ; picks cap0->inf boundaries (n=180m) with w512 frames n and n+5/n+10."""
import os, sys
from PIL import Image, ImageDraw, ImageChops, ImageStat
d, out = sys.argv[1], sys.argv[2]
def f(n): p = f"{d}/fb_{n:07d}_w512.ppm"; return p if os.path.exists(p) else None
rows = []
for m in range(4, 26):
    b = 180*m
    a, c = f(b), f(b+10)
    if a and c:
        ia, ic = Image.open(a).convert('RGB'), Image.open(c).convert('RGB')
        diff = sum(ImageStat.Stat(ImageChops.difference(ia, ic)).mean)/3
        rows.append((diff, b, ia, ic))
rows.sort(key=lambda r: r[0])
for r in [x for x in rows if x[1] >= 3000][:6]: print(f"n={r[1]} meanabsdiff={r[0]:.1f}")
r = [x for x in rows if x[1] == int(os.environ.get('PAIR','2700'))][0]; w, h = 640, 448
s = Image.new('RGB', (w*2+18, h+40), (30, 30, 30)); dr = ImageDraw.Draw(s)
for i, (t, im) in enumerate([(f"cap0 n={r[1]}", r[2]), (f"cap-inf n={r[1]+10} (same run)", r[3])]):
    dr.text((6+i*(w+6), 6), t, fill=(255, 255, 0)); s.paste(im.resize((w, h)), (6+i*(w+6), 24))
s.save(out)
