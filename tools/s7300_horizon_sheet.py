#!/usr/bin/env python3
"""s7300 G1c: horizon-in-view dd look sheet. Same shots/crop/fog% score as tools/s7295_dd_look_sheet.py, but columns are
SELECTED: per level group, the seconds where the group's first arm (the dd1 reference) shows the most sky band (horizon in
view; s7295's fixed window t=100-140 was a bank under cliffs with the horizon off-frame). Every arm of a group ran the same
autopilot timeline, so column k is the same route second in each arm.
Verdict per group on the selected columns (NEXT s7300): H-none-in-view if the ref arm never reaches IN_VIEW fog%;
H-more if the last arm (dd-max) is >=3 points below the middle arm; H-same if |last-middle| < 3 while ref-middle >= 3.
Controls: painted lower band raises fog% (CONTROL PASS), and ref > middle on the selected columns (real-scene control).
usage: s7300_horizon_sheet.py DIR out.jpg GROUP [GROUP ...]   GROUP = name=arm1,arm2,arm3   env TOPN=5 IN_VIEW=8 SECS=90,100,..."""
import sys, re, glob, os
from PIL import Image, ImageDraw
d, out, groups = sys.argv[1], sys.argv[2], [g.split('=', 1) for g in sys.argv[3:]]
TOPN = int(os.environ.get('TOPN', 5)); INV = float(os.environ.get('IN_VIEW', 8))
SECS = [s for s in os.environ.get('SECS', '').split(',') if s]
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
def shots(a):
    ps = glob.glob(f'{d}/shot_{a}_c*.png'); m = {int(re.search(r'_c(\d+)\.png$', p)[1]): p for p in ps}; return m
rows = []; ctl = None; mean = lambda v: sum(v) / max(1, len(v))
for name, arms in groups:
    arms = arms.split(','); S = {a: shots(a) for a in arms}
    ks = sorted(set.intersection(*[set(S[a]) for a in arms]))
    ims = {a: {k: crop(a, S[a][k]) for k in ks} for a in arms}; sc = {a: {k: fog(ims[a][k]) for k in ks} for a in arms}
    if ctl is None and ks:
        c = ims[arms[0]][ks[0]].copy(); w, h = c.size; sky = c.getpixel((w // 2, int(h * .13)))
        ImageDraw.Draw(c).rectangle((0, int(h * .31), w, h // 2), fill=sky); ctl = (sc[arms[0]][ks[0]], fog(c))
        print(f'control ({arms[0]} c{ks[0]}): fog% {ctl[0]:.1f} -> painted {ctl[1]:.1f}', 'CONTROL PASS' if ctl[1] > ctl[0] + 5 else 'CONTROL FAIL')
    for a in arms: print(f'{name} {a}: all fog% ' + ' '.join(f'{sc[a][k]:.0f}' for k in ks) + f' | mean {mean(list(sc[a].values())):.1f}')
    sel = sorted(sorted(ks, key=lambda k: -sc[arms[0]][k])[:TOPN]); sel = [k for k in sel if sc[arms[0]][k] >= INV]
    lab = lambda k: f't={SECS[k-1]}' if k - 1 < len(SECS) else f'c{k}'
    print(f'{name} selected (ref {arms[0]} fog% >= {INV}, top {TOPN}): ' + (' '.join(lab(k) for k in sel) or 'none'))
    m = {a: mean([sc[a][k] for k in sel]) for a in arms}
    print(f'{name} selected means: ' + ' '.join(f'{a} {m[a]:.1f}' for a in arms))
    if not sel: v = 'H-none-in-view'
    else:
        r, mid, top = m[arms[0]], m[arms[-2]], m[arms[-1]]
        v = 'H-more' if mid - top >= 3 else ('H-same' if abs(top - mid) < 3 and r - mid >= 3 else 'unresolved (real-scene control ref-mid < 3)')
        print(f'{name} real-scene control ref-mid {r - mid:+.1f}', 'PASS' if r - mid >= 3 else 'FAIL')
    print(f'{name} verdict: {v}')
    for a in arms: rows.append((f'{name} {a}', [(lab(k), ims[a][k], sc[a][k]) for k in sel]))
TW = 400; th = lambda i: i.resize((TW, int(TW * i.height / i.width)))
C = max(1, max(len(r[1]) for r in rows)); TH = max([th(i).height for r in rows for _, i, _ in r[1]] or [200]) + 16
sh = Image.new('RGB', (TW * C, TH * len(rows)), (20, 20, 20)); dr = ImageDraw.Draw(sh)
for j, (a, cells) in enumerate(rows):
    for k, (l, i, v) in enumerate(cells):
        sh.paste(th(i), (k * TW, j * TH + 16)); dr.text((k * TW + 4, j * TH + 2), f'{a} {l} fog {v:.0f}%', fill=(255, 255, 0))
sh.save(out, quality=85); print('wrote', out)
