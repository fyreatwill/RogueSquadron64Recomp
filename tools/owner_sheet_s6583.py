#!/usr/bin/env python3
"""s6583 tagged pair sheet: uses [fbdump] dd= tags. Usage: owner_sheet_s6583.py run.log fbd_dir out.png
Pairs consecutive dumps (n, n+5) with opposite dd tag; ranks by mean abs diff over the bottom (ship/HUD) 40% strip."""
import os, re, sys, glob
from PIL import Image, ImageDraw, ImageChops, ImageStat
log, d, out = sys.argv[1:4]
tag = {int(m.group(1)): int(m.group(2)) for m in re.finditer(r'\[fbdump\] n=(\d+) .* dd=(\d)', open(log).read())}
def img(n):
    g = glob.glob(f"{d}/fb_{n:07d}_w*.ppm"); return Image.open(g[0]).convert('RGB') if g else None
rows = []
for n in sorted(tag):
    m = n + 5
    if m in tag and tag[n] != tag[m] and n > 600:
        a, b = img(n), img(m)
        if a is None or b is None or a.size != b.size: continue
        w, h = a.size; box = (0, int(h*.6), w, h)
        diff = sum(ImageStat.Stat(ImageChops.difference(a.crop(box), b.crop(box))).mean)/3
        rows.append((diff, n, m, a, b))
rows.sort(key=lambda r: r[0])
for r in rows[:6]: print(f"n={r[1]}(dd{tag[r[1]]}) -> {r[2]}(dd{tag[r[2]]}) strip_diff={r[0]:.1f}")
print("pairs:", len(rows))
sel = [r for r in rows if r[0] >= 1.0][:3]
w, h = 480, 336
s = Image.new('RGB', (w*2+18, (h+22)*len(sel)+4), (30, 30, 30)); dr = ImageDraw.Draw(s)
for k, (diff, n, m, a, b) in enumerate(sel):
    if tag[n] == 1: a, b, n, m = b, a, m, n   # dd=0 is retail (multiplier off), dd=1 is dd4
    for i, (t, im) in enumerate([(f"retail dd1 n={n}", a), (f"dd4 n={m}", b)]):
        dr.text((6+i*(w+6), 4+k*(h+22)), t, fill=(255, 255, 0)); s.paste(im.resize((w, h)), (6+i*(w+6), 18+k*(h+22)))
s.save(out)
