#!/usr/bin/env python3
"""s7207: s7183 BOB-model field score per swap, grouped by the background photo of the Elite Rogues slideshow, so two runs at
different slideshow phases compare like with like. Photo signature = mean RGB of the list-free right strip (native x 440-511,
y 300-440) of the angrylion NOPREFILL replay, clustered greedily (L1 < 18). Prints, per photo cluster, n swaps and median d(P,BOB)
per arm (best of pframe +-REP). usage: s7207_parity_byphoto.py RECT S0 S1 ARM1 [ARM2 ...]  (files scratch/s7141/<ARM>{.raw,C.frames.csv,r,n})"""
import sys, os, csv, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s7122_fidelity import Raw
from s7183_parity import parity, rgb, double, rowd
from PIL import Image, ImageStat
rect = tuple(map(int, sys.argv[1].split(','))); s0, s1 = int(sys.argv[2]), int(sys.argv[3]); arms = sys.argv[4:]; REP = int(os.environ.get('REP', '2'))
cent = []; out = {}
def cid(sig):
    for i, c in enumerate(cent):
        if sum(abs(a - b) for a, b in zip(c, sig)) < 18: return i
    cent.append(sig); return len(cent) - 1
for A in arms:
    raw = Raw(f'scratch/s7141/{A}.raw'); D = f'scratch/s7141/{A}'
    for r in csv.DictReader(open(f'{D}C.frames.csv')):
        s = int(r['swap'])
        if not s0 <= s <= s1 or not os.path.exists(f'{D}r/f{s}.rgb'): continue
        cur, c = parity(f'{D}r/f{s}.rgb')
        if min(c) * 4 > max(c): continue
        w, h, px = rgb(f'{D}n/f{s}.rgb'); h = min(h, 448); W = Image.frombytes('RGB', (w, h), px[:w * h * 3]); B = double(W, cur)
        sig = tuple(ImageStat.Stat(W.crop((440, 300, 511, 440))).mean); k = cid(sig); j0 = int(r['pframe'])
        best = min(rowd(raw.img(j).crop(rect).resize((w, h), Image.BOX), B, cur)[2] for j in range(max(0, j0 - REP), min(len(raw.T), j0 + REP + 1)))
        out.setdefault(k, {}).setdefault(A, []).append(best)
print('photo  sig(R,G,B)        ' + '  '.join(f'{A:>14s}' for A in arms))
for k in sorted(out):
    print(f'{k:3d}  {tuple(round(x) for x in cent[k])!s:18s}' + '  '.join(f'n{len(out[k].get(A, [])):3d} d {statistics.median(out[k][A]):5.2f}' if A in out[k] else f'{"-":>14s}' for A in arms))
