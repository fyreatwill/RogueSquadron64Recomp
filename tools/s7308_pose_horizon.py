#!/usr/bin/env python3
"""s7308 G1c: same-pose horizon score + owner sheet for tools/g3_optin_pose_arms.sh output (POSE_FREEZE window captures).
Per freeze k and arm: sky% (pixels within 24 of the sky colour sampled at 13% height, rows 12%-50%: the s7300 fog% score) and the
mean abs RGB diff of the horizon band (BAND, default rows 30%-58%) vs a reference arm. Noise floor = REPEAT pair (same settings twice), positive control = CTL pair
(dd1 vs dd6, must exceed the floor by x3). Verdict per pair of interest (dd6 vs dd8, dd8 vs dd8f) relative to the floor.
usage: s7308_pose_horizon.py DIR out.jpg ARMS(comma) REPEAT=a,b CTL=a,b PAIRS=a,b;c,d"""
import sys, glob, os, re
from PIL import Image, ImageDraw, ImageChops, ImageStat
d, out, arms = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
kv = dict(a.split('=', 1) for a in sys.argv[4:])
Y0, Y1 = (float(x) for x in os.environ.get('BAND', '0.30,0.58').split(','))  # horizon band (s7308 L1 freeze: horizon ~0.50)
def load(a, k):
    ps = sorted(glob.glob(f'{d}/{a}/f{k}_*.png'))
    if not ps: return None
    im = Image.open(ps[-1]).convert('RGB'); w, h = im.size
    # drop the title bar (window capture): first rows that are not game content; title bar ~ 28pt (56 px at 2x)
    tb = 64 if h > 900 else 32  # measured s7308: 2x window capture title bar = 64 px
    im = im.crop((0, tb, w, h))
    # trim black bars
    bb = im.point(lambda v: 255 if v > 12 else 0).convert('L').getbbox()
    return im.crop(bb) if bb else im
def sky(im):
    w, h = im.size; px = im.load(); s = px[w // 2, int(h * .13)]; t = hit = 0
    for y in range(int(h * .12), h // 2, max(1, h // 120)):
        for x in range(0, w, max(1, w // 160)):
            q = px[x, y]; t += 1; hit += abs(q[0]-s[0]) + abs(q[1]-s[1]) + abs(q[2]-s[2]) <= 24
    return 100 * hit / max(1, t)
def edge(im, thr=110):
    # far-terrain top edge: per column (5-95% width, skipping the HUD radar/lives corners), the first row below 30% height whose
    # luminance < thr; median as a fraction of height (smaller = higher on screen = ground drawn farther). s7308.
    g = im.convert('L'); w, h = g.size; px = g.load(); r = []
    for x in range(int(w * .2), int(w * .8), max(1, w // 120)):
        for y in range(int(h * .3), h):
            if px[x, y] < thr: r.append(y / h); break
    r.sort(); return r[len(r) // 2] if r else 1.0
def diff(a, b):
    b = b.resize(a.size); w, h = a.size; box = (0, int(h * Y0), w, int(h * Y1))
    return sum(ImageStat.Stat(ImageChops.difference(a.crop(box), b.crop(box))).mean) / 3
ks = sorted({int(re.search(r'/f(\d+)_', p)[1]) for p in glob.glob(f'{d}/*/f*_*.png')})
I = {a: {k: load(a, k) for k in ks} for a in arms}
ok = [k for k in ks if all(I[a][k] is not None for a in arms)]
for k in ok: print(f'k={k} edge(rows/1000, lower=farther): ' + ' '.join(f'{a} {1000*edge(I[a][k]):.0f}' for a in arms) + ' | sky%: ' + ' '.join(f'{a} {sky(I[a][k]):.1f}' for a in arms) + ' | size ' + ' '.join(f'{a}:{I[a][k].size[0]}x{I[a][k].size[1]}' for a in arms[:1]))
def pd(p): a, b = p.split(','); return [diff(I[a][k], I[b][k]) for k in ok]
m = lambda v: sum(v) / max(1, len(v))
fl = pd(kv['REPEAT']); ct = pd(kv['CTL'])
print(f"floor {kv['REPEAT']}: " + ' '.join(f'{x:.2f}' for x in fl) + f' mean {m(fl):.2f}')
print(f"control {kv['CTL']}: " + ' '.join(f'{x:.2f}' for x in ct) + f' mean {m(ct):.2f} ' + ('CONTROL PASS' if m(ct) > 3 * max(m(fl), 0.3) else 'CONTROL FAIL'))
for p in kv.get('PAIRS', '').split(';'):
    if not p: continue
    v = pd(p); r = m(v) / max(m(fl), 0.3)
    print(f'pair {p}: ' + ' '.join(f'{x:.2f}' for x in v) + f' mean {m(v):.2f} = x{r:.1f} floor -> ' + ('DIFFERS' if r >= 3 else 'SAME (within x3 floor)'))
W = 480; rows = []
for a in arms:
    ims = [I[a][k].resize((W, int(W * I[a][k].size[1] / I[a][k].size[0]))) for k in ok]; rows.append((a, ims))
H = max(im.size[1] for _, ims in rows for im in ims); S = Image.new('RGB', (90 + W * len(ok), H * len(rows)), 'black'); D = ImageDraw.Draw(S)
for r, (a, ims) in enumerate(rows):
    D.text((4, r * H + 4), a, fill='white')
    for c, im in enumerate(ims): S.paste(im, (90 + c * W, r * H)); D.text((94 + c * W, r * H + 4), f'k{ok[c]} sky {sky(I[a][ok[c]]):.0f}%', fill='yellow')
S.save(out, quality=88); print('sheet', out, S.size)
