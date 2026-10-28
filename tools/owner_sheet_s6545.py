#!/usr/bin/env python3
"""Owner contact sheet: lvl1 pinned pose, retail / dd2 / dd4 cap0 / dd4 cap-inf (s6545).
Same VI frame number (3300) across arms; pose is pinned by the s6544 recipe."""
import glob
from PIL import Image, ImageDraw
M = 'scratch/agent/m6/g1_lvl1s6544_'
arms = [('retail', 'retail'), ('dd2', 'DRAW_DISTANCE=2'), ('dd4', 'DD=4 cap0 (default)'), ('dd4inf', 'DD=4 cap-inf')]
FR = 3300
cells = []
for a, t in arms:
    fs = glob.glob(f'{M}{a}/fbd/fb_*_w*.ppm')
    f = min(fs, key=lambda p: abs(int(p.split('fb_')[1][:7]) - FR))
    cells.append((t, f))
w, h = 640, 448
pad, lab = 6, 16
sheet = Image.new('RGB', (w * 2 + pad * 3, (h + lab) * 2 + pad * 3), (30, 30, 30))
d = ImageDraw.Draw(sheet)
for i, (t, f) in enumerate(cells):
    r, c = divmod(i, 2)
    x = pad + c * (w + pad); y = pad + r * (h + lab + pad)
    d.text((x, y), f'{t}  {f.split("/")[-1]}', fill=(255, 255, 0))
    sheet.paste(Image.open(f).convert('RGB').resize((w, h)), (x, y + lab))
    print(t, f)
sheet.save('docs/owner_sheet_s6545.png')
