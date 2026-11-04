#!/usr/bin/env python3
"""s6879 G3: does a wide arm's centre match a 4:3 arm at the same pose? Window PNGs from tools/g3_optin_pose_arms.sh, P3 -> sRGB.

Per freeze k, fits x scale and offset, y scale and offset mapping the 4:3 picture into the wide picture (coarse grid on a small copy,
then refined), and reports MAD over the overlap with the HUD bands excluded. --ctl ARM scores another 4:3 arm through the same fit:
it must land far above the base arm, or a low score says nothing. The 4:3 window pillarboxes, so its picture is cropped to the non-black box first.
Scored region = below the top third, minus the lives corner, so radar and craft icon never count (they move by design).
MAD is blind to a lost far terrain band (s6879: fx1 restored the horizon and MAD moved 20.66 -> 19.00), so hz_mean/hz_p90 compare the terrain top per column, in 4:3 window pixels. Read hz_p90: craft and cloud gaps swamp hz_mean (k2 w169 16.99 vs fx1 0.63).
s6882: --pin takes the fit from window geometry instead: sx = sy = wide height / 4:3 picture height, centred, only ox and oy refined. Use it at 21:9: the free grid's sy starts at
1.50 and the right 21:9 value is ~1.24, so the free fit cannot reach it (s6880 sx 1.22, sy 1.48). --scan prints MAD over a scale sweep, to check the geometry value is the minimum.
Usage: g3_aspect_crop.py ARMS_DIR BASE WIDE [--ctl ARM] [--bar N] [--pin] [--scan]"""
import os, sys
from PIL import Image, ImageChops, ImageStat
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_oracle_match import to_srgb
THR = 32

def rgb(root, arm, k, bar, crop=False):
    im = to_srgb(Image.open(os.path.join(root, arm, 'f%d_1.png' % k)).convert('RGB'))
    im = im.crop((0, bar + (2 if crop else 0), im.width, im.height))  # s6882: 2 title rows survive --bar 62 and span the width, so without +2 the bbox kept the pillarbox bars
    return im.crop(im.convert('L').point(lambda v: 255 if v > 8 else 0).getbbox()) if crop else im

def lum(root, arm, k, bar, crop=False):
    return rgb(root, arm, k, bar, crop).convert('L')

def horizon(a, w, p):
    """(mean, p90) |terrain top difference| per column, in 4:3 window pixels, over the box the 4:3 picture covers. Top = walking up from the bottom,
    the first row of blue sky, so grey cloud never counts as ground."""
    sx, ox, sy, oy = p
    x0, x1 = max(0, int(ox)), min(w.width, int(ox + sx * a.width))
    y0, y1 = max(0, int(oy)), min(w.height, int(oy + sy * a.height))
    v = a.transform((x1 - x0, y1 - y0), Image.AFFINE, (1 / sx, 0, (x0 - ox) / sx, 0, 1 / sy, (y0 - oy) / sy), Image.BILINEAR)
    def top(im):
        q = im.load(); h = im.height; t = []
        for x in range(im.width):
            y = h - 1
            while y >= 0 and (q[x, y][2] <= max(q[x, y][0], q[x, y][1]) + 8 or q[x, y][2] < 120): y -= 1
            t.append(h - 1 - y)
        return t
    d = sorted(abs(i - j) / sy for i, j in zip(top(v), top(w.crop((x0, y0, x1, y1)))))
    d = d[:len(d) * 95 // 100]  # the worst 5% = craft and reticle columns
    return sum(d) / len(d), d[len(d) * 9 // 10]

def score(a, w, p, full=False):
    """MAD inside the wide-frame box the 4:3 picture covers, HUD corners out; full=True returns (mad, fraction > THR, diff bbox)"""
    sx, ox, sy, oy = p
    x0, x1 = max(0, int(ox)), min(w.width, int(ox + sx * a.width))
    y0, y1 = max(0, int(oy)), min(w.height, int(oy + sy * a.height))
    bw, bh = x1 - x0, y1 - y0; y0 += bh // 3; bh = y1 - y0
    if bw < 40 or bh < 20: return 1e9
    v = a.transform((bw, bh), Image.AFFINE, (1 / sx, 0, (x0 - ox) / sx, 0, 1 / sy, (y0 - oy) / sy), Image.BILINEAR)
    d = ImageChops.difference(v, w.crop((x0, y0, x1, y1)))
    d.paste(0, (0, bh * 7 // 10, bw * 22 // 100, bh))
    m = ImageStat.Stat(d).mean[0]
    if not full: return m
    t = d.point(lambda q: 255 if q > THR else 0)
    return m, ImageStat.Stat(t).mean[0] / 255, t.getbbox()

def fit(a, w):
    f = 4; a2 = a.resize((a.width // f, a.height // f), Image.BOX); w2 = w.resize((w.width // f, w.height // f), Image.BOX); best = (1e9, None)
    for i in range(60):
        sx = 1.15 + i * 0.01
        for j in range(20):
            sy = 1.50 + j * 0.01
            ox0 = (w2.width - sx * a2.width) / 2; oy0 = (w2.height - sy * a2.height) / 2
            for dy in (-4, -2, 0, 2, 4):
                s = score(a2, w2, (sx, ox0, sy, oy0 + dy))
                if s < best[0]: best = (s, (sx, ox0 * f, sy, (oy0 + dy) * f))
    p = list(best[1]); s = score(a, w, p)
    for ds, dp in ((0.004, 2), (0.001, 1), (0.0004, 0.5)):
        for _ in range(8):
            for i, d in enumerate((ds, dp, ds, dp)):
                for sg in (-d, d):
                    q = list(p); q[i] += sg; t = score(a, w, q)
                    if t < s: s, p = t, q
    return s, p

def pinned(a, w):
    """s6882: one scale from geometry, centred; offsets refined, never the scale"""
    k = w.height / a.height; p = [k, (w.width - k * a.width) / 2, k, 0.0]; s = score(a, w, p)
    for dp in (8, 4, 2, 1, 0.5):
        for _ in range(8):
            for i in (1, 3):
                for sg in (-dp, dp):
                    q = list(p); q[i] += sg; t = score(a, w, q)
                    if t < s: s, p = t, q
    return s, p

def main():
    a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    root, base = a[0], a[1]; wides = a[2].split(','); ctl = opt('--ctl', None); bar = int(opt('--bar', 62))
    print('arm      k   mad  frac>T hz_mean hz_p90  sx     ox     sy     oy   ctl_mad')
    P = {}
    for wide in wides:
        for k in range(3):
            A, Wd = lum(root, base, k, bar, True), lum(root, wide, k, bar)
            if '--scan' in a:
                g = A.height and Wd.height / A.height
                print('scan %s k%d geom %.3f: ' % (wide, k, g) + ' '.join('%.3f=%.2f' % (g * f, score(A, Wd, (g * f, (Wd.width - g * f * A.width) / 2, g * f, (Wd.height - g * f * A.height) / 2))) for f in (0.85, 0.9, 0.95, 0.98, 1, 1.02, 1.05, 1.1, 1.15, 1.2, 1.28)))
            if k not in P: P[k] = (pinned if '--pin' in a else fit)(A, Wd)[1]  # one fit per k, from the first wide arm, so arms stay comparable
            p = P[k]; m, fr, bb = score(A, Wd, p, True)
            c = score(lum(root, ctl, k, bar, True), Wd, p) if ctl else float('nan')
            hm, hp = horizon(rgb(root, base, k, bar, True), rgb(root, wide, k, bar), p)
            print('%-8s %d %6.2f %6.4f %6.2f %6.2f %6.3f %6.1f %6.3f %6.1f %7.2f' % (wide, k, m, fr, hm, hp, p[0], p[1], p[2], p[3], c))

if __name__ == '__main__': main()
