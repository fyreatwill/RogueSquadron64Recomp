#!/usr/bin/env python3
"""Owner contact sheet: lvl1 flight at 4:3/16:9/21:9 + hangar 16:9/21:9 (s6439)."""
import glob, sys
from PIL import Image, ImageDraw
M = 'scratch/agent/m6/'
def score(f):
    # clean frame: non-black, smooth bottom quarter (readback garbage is high-frequency)
    im = Image.open(f).convert('L'); w, h = im.size
    px = im.load(); xs = range(0, w, 4)
    mean = sum(px[x, y] for y in range(0, h, 8) for x in xs) / (len(xs) * (h // 8))
    bot = [sum(abs(px[x, y] - px[x, y + 1]) for x in xs) / len(xs) for y in range(h * 3 // 4, h - 1, 3)]
    return -1 if mean < 20 else -sum(bot) / len(bot)
def pick(d, w, n):
    fs = sorted(glob.glob(f'{M}{d}/fbd/fb_*_w{w}.ppm'))
    fs = [f for f in fs if int(f.split('fb_')[1][:7]) >= 2000][::6]
    return max(fs, key=score)
cells = [('flight 4:3 (640x448)', pick('g1_lvl1s6428_a43', 640, 600)),
         ('flight 16:9 (796x448)', pick('g1_lvl1s6428_a169', 796, 600)),
         ('flight 21:9 (1024x448)', pick('g1_lvl1s6428_a219', 1024, 600)),
         ('hangar 16:9', pick('s6434_hangar_16x9', 796, 3)),
         ('hangar 21:9', pick('s6434_hangar_21x9', 1024, 3))]
H = 448; pad = 6; lab = 16
W = 1024 * 3 + pad * 4
sheet = Image.new('RGB', (W, (H + lab) * 2 + pad * 3), (30, 30, 30))
d = ImageDraw.Draw(sheet)
for i, (t, f) in enumerate(cells):
    im = Image.open(f).convert('RGB')
    r, c = divmod(i, 3)
    x = pad + c * (1024 + pad); y = pad + r * (H + lab + pad)
    d.text((x, y), f'{t}  {f.split("/")[-1]}', fill=(255, 255, 0))
    sheet.paste(im, (x, y + lab))
    print(t, f, im.size)
sheet.save('docs/owner_sheet_s6439.png')
