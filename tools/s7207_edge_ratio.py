#!/usr/bin/env python3
"""s7207: presented sharpness vs angrylion on field swaps, split by direction. Per swap: P = presented crop box-scaled to native 512x448,
A = BOB of the NOPREFILL replay (current field line-doubled). ev = mean |row-to-row| diff, eh = mean |col-to-col| diff. Ratio P/A per
direction; a vertical-only resample (half-row offset, field blend) lowers ev/ev_A but not eh/eh_A.
usage: s7207_edge_ratio.py RECT S0 S1 ARM...   (also reports the same on 1 px vertically box-blurred A as a positive control)"""
import sys, os, csv, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s7122_fidelity import Raw
from s7183_parity import parity, rgb, double
from PIL import Image, ImageChops, ImageStat
rect = tuple(map(int, sys.argv[1].split(','))); s0, s1 = int(sys.argv[2]), int(sys.argv[3])
def e(im):
    g = im.convert('L'); w, h = g.size
    v = ImageStat.Stat(ImageChops.difference(g.crop((0, 0, w, h - 1)), g.crop((0, 1, w, h)))).mean[0]
    hh = ImageStat.Stat(ImageChops.difference(g.crop((0, 0, w - 1, h)), g.crop((1, 0, w, h)))).mean[0]
    return v, hh
for A in sys.argv[4:]:
    raw = Raw(f'scratch/s7141/{A}.raw'); D = f'scratch/s7141/{A}'; rv = []; rh = []; cv = []
    for r in csv.DictReader(open(f'{D}C.frames.csv')):
        s = int(r['swap'])
        if not s0 <= s <= s1 or not os.path.exists(f'{D}r/f{s}.rgb') or s % 3: continue
        cur, c = parity(f'{D}r/f{s}.rgb')
        if min(c) * 4 > max(c): continue
        w, h, px = rgb(f'{D}n/f{s}.rgb'); h = min(h, 448); B = double(Image.frombytes('RGB', (w, h), px[:w * h * 3]), cur)
        P = raw.img(int(r['pframe'])).crop(rect).resize((w, h), Image.BOX)
        pv, ph = e(P); av, ah = e(B); bv, _ = e(B.resize((w, h // 2), Image.BOX).resize((w, h), Image.BILINEAR))
        if av < 0.5 or ah < 0.5: continue
        rv.append(pv / av); rh.append(ph / ah); cv.append(bv / av)
    m = statistics.median
    print(f'{A}: n={len(rv)} presented/AL edge ratio vertical {m(rv):.3f} horizontal {m(rh):.3f}  (control: AL v-blurred vertical ratio {m(cv):.3f})')
