#!/usr/bin/env python3
"""s7223: score WINDOWED RETINA arms from full-desktop screencapture -x shots (2x built-in, pixels = 2 x points).
The window's content rect comes from the run log's last "[g1f] window WxH fullscreen=0 at X,Y" row (points). Per shot:
  bbox  = lit extent (rows/cols with >2% pixels above luma 24) inside the window crop, as a fraction of the crop
          (H-letter: a points-sized viewport in a 2x chain shows as ~0.5 x 0.5 or an offset bbox);
  hf    = s7203 half-res residual mean|I-up2(down2(I))| / mean|I-shift1(I)| over the central 80% of the crop
          (backing-pixel chain scores higher than a point chain upscaled by CoreAnimation).
Positive controls (printed per arm): hf of the first scored shot after a 2x down/up resample (must fall toward the
RETINA=0 level), and bbox of that shot with its left half blanked (must report x0 >= 0.45).
usage: s7223_window_score.py DIR ARM [ARM ...]   (expects DIR/shot_ARM_T.png and DIR/log_ARM.txt)"""
import sys, re, glob
from PIL import Image, ImageChops, ImageStat
d = sys.argv[1]
def m(i): return ImageStat.Stat(i).mean[0]
def hf(a):
    w, h = a.size; a = a.crop((w // 10, h // 10, w - w // 10, h - h // 10)); w, h = a.size
    if ImageStat.Stat(a).stddev[0] < 2: return None
    rt = a.resize((w // 2, h // 2), Image.BOX).resize((w, h), Image.BILINEAR)
    return m(ImageChops.difference(a, rt)) / max(m(ImageChops.difference(a, ImageChops.offset(a, 1, 0))), 1e-6)
def bbox(a):
    s = a.resize((a.size[0] // 4, a.size[1] // 4), Image.BOX); W, H = s.size; p = s.load()
    rows = [y for y in range(H) if sum(p[x, y] > 24 for x in range(W)) > 0.02 * W]
    cols = [x for x in range(W) if sum(p[x, y] > 24 for y in range(H)) > 0.02 * H]
    return (round(cols[0] / W, 3), round(rows[0] / H, 3), round((cols[-1] + 1) / W, 3), round((rows[-1] + 1) / H, 3)) if rows and cols else None
for arm in sys.argv[2:]:
    log = open(f'{d}/log_{arm}.txt', errors='replace').read()
    w = re.findall(r'\[g1f\] window (\d+)x(\d+) fullscreen=0 at (-?\d+),(-?\d+)', log)
    sc = re.findall(r'\[retina\] swapchain create (\d+)x(\d+)[^\n]*', log)
    dr = re.findall(r'\[g1f\] drawable (\d+)x(\d+)', log)
    print(f'== {arm}: window(pt) {w[-1] if w else None}  drawable {dr[-1] if dr else None}  swapchain {sc[-1] if sc else None}')
    if not w: continue
    W, H, X, Y = (int(v) for v in w[-1]); box = (2 * X, 2 * Y, 2 * (X + W), 2 * (Y + H))
    ts = sorted(int(re.search(r'_(\d+)\.png', p)[1]) for p in glob.glob(f'{d}/shot_{arm}_*.png'))
    vals = []; first = None
    for t in ts:
        a = Image.open(f'{d}/shot_{arm}_{t}.png').convert('L').crop(box)
        b, h = bbox(a), hf(a)
        if h is not None:
            vals.append(h); first = first or a
        print(f'  t={t:3d} bbox {b}  hf {"-" if h is None else "%.3f" % h}')
    if vals: print(f'  hf mean {sum(vals) / len(vals):.3f} over {len(vals)} shots')
    if first:
        w2, h2 = first.size
        ctl = first.resize((w2 // 2, h2 // 2), Image.BOX).resize((w2, h2), Image.BILINEAR)
        bl = first.copy(); bl.paste(0, (0, 0, w2 // 2, h2))
        cb = bbox(bl)
        print(f'  CONTROL hf down/up2 {hf(ctl):.3f} (vs {hf(first):.3f}); blank-left bbox {cb} ->',
              'PASS' if cb and cb[0] >= 0.45 and hf(ctl) < hf(first) else 'FAIL')
