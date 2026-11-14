#!/usr/bin/env python3
"""s7295 G1c: owner look sheet + far-terrain score across draw-distance arms from windowed screencapture -x shots
(tools/g1e_owner_quiet_arms.zsh SHOTS=..., same autopilot timeline in every arm, so column k = same route second).
The game picture is cropped from the full-desktop shot with the run log's last "[g1f] window WxH fullscreen=0 at X,Y"
(points; pixel scale 2 when the 2x crop fits the shot, else 1).
Score per shot: fog% = share of pixels in the band 12%..50% of the crop height whose colour is within 24 (L1) of the sky
colour sampled at 13% height, centre (more far terrain drawn -> fewer sky/haze pixels above the horizon). Cross-run: the
camera is not pixel-identical, so read the means, not single cells.
Positive control (printed): the first scored shot with the band's lower half painted sky colour must score higher
(CONTROL PASS); a dd1 arm, when given, is the real-scene control (its fog% should exceed the dd>1 arms on the same level).
usage: s7295_dd_look_sheet.py DIR out.png ARM [ARM ...]"""
import sys, re, glob
from PIL import Image, ImageDraw
d, out, arms = sys.argv[1], sys.argv[2], sys.argv[3:]
def crop(arm, p):
    log = open(f'{d}/log_{arm}.txt', errors='replace').read()
    w = re.findall(r'\[g1f\] window (\d+)x(\d+) fullscreen=0 at (-?\d+),(-?\d+)', log)
    im = Image.open(p).convert('RGB')
    if not w: return im
    W, H, X, Y = map(int, w[-1]); s = 2 if (X + W) * 2 <= im.width and (Y + H) * 2 <= im.height else 1
    return im.crop((X * s, Y * s, (X + W) * s, (Y + H) * s))
def fog(im):
    w, h = im.size; px = im.load(); sky = px[w // 2, int(h * .13)]; tot = hit = 0
    for y in range(int(h * .12), h // 2, max(1, h // 120)):
        for x in range(0, w, max(1, w // 160)):
            q = px[x, y]; tot += 1; hit += abs(q[0] - sky[0]) + abs(q[1] - sky[1]) + abs(q[2] - sky[2]) <= 24
    return 100 * hit / max(1, tot)
rows = []; ctl = None
for a in arms:
    shots = sorted(glob.glob(f'{d}/shot_{a}_c*.png'), key=lambda p: int(re.search(r'_c(\d+)\.png$', p)[1]))
    ims = [crop(a, p) for p in shots]; sc = [fog(i) for i in ims]
    if ctl is None and ims:
        c = ims[0].copy(); w, h = c.size; sky = c.getpixel((w // 2, int(h * .13)))
        ImageDraw.Draw(c).rectangle((0, int(h * .31), w, h // 2), fill=sky); ctl = (sc[0], fog(c))
        print(f'control ({a} c1): fog% {ctl[0]:.1f} -> painted {ctl[1]:.1f}', 'CONTROL PASS' if ctl[1] > ctl[0] + 5 else 'CONTROL FAIL')
    print(f'{a}: shots={len(ims)} fog% ' + ' '.join(f'{v:.1f}' for v in sc) + f' | mean {sum(sc)/max(1,len(sc)):.1f}')
    rows.append((a, ims, sc))
TW = 480; th = lambda i: i.resize((TW, int(TW * i.height / i.width)))
C = max(len(r[1]) for r in rows); TH = max(th(i).height for r in rows for i in r[1]) + 16
sh = Image.new('RGB', (TW * C, TH * len(rows)), (20, 20, 20)); dr = ImageDraw.Draw(sh)
for j, (a, ims, sc) in enumerate(rows):
    for k, (i, v) in enumerate(zip(ims, sc)):
        sh.paste(th(i), (k * TW, j * TH + 16)); dr.text((k * TW + 4, j * TH + 2), f'{a} shot {k+1} fog {v:.0f}%', fill=(255, 255, 0))
sh.save(out); print('wrote', out)
