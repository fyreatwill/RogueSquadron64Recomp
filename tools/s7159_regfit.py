#!/usr/bin/env python3
"""s7159 registration check for a G3 owner-recipe fidelity capture (run BEFORE deleting <N>.raw / <N>r).
usage: s7159_regfit.py <dir> <name> [rect=0,9,369,216] [nsample=16]
Picks nsample swaps from <name>.frames.csv, then per box (whole inner frame, centre 3D, radar, lives, top-left icon)
prints the integer (dx,dy) shift of the presented crop that minimises median mean|d| against angrylion (resized to rect).
If the whole-frame best is not (0,0) the s7141 score is registration-limited: refit the rect (s7122_fidelity score --rect)
before calling a level H-level. Boxes wanting DIFFERENT shifts = HUD placed differently from the 3D view (or a scale term).
s7159: L12 centre wanted (0,1)/(1,1) (frac 0.020 -> 0.010 centre after refit 1,10,370,217), radar (1,0), lives (0,2), icon (0,0)."""
import csv, importlib.util, os, random, sys
from PIL import Image, ImageChops, ImageStat
spec = importlib.util.spec_from_file_location('F', os.path.join(os.path.dirname(__file__), 's7122_fidelity.py'))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
D, N = sys.argv[1], sys.argv[2]
R = tuple(map(int, (sys.argv[3] if len(sys.argv) > 3 else '0,9,369,216').split(',')))
K = int(sys.argv[4]) if len(sys.argv) > 4 else 16
W, H = R[2] - R[0], R[3] - R[1]
raw = F.Raw(os.path.join(D, N + '.raw'))
rows = list(csv.DictReader(open(os.path.join(D, N + '.frames.csv'))))[1:-1]
random.seed(7159); pick = random.sample(rows, min(K, len(rows)))
P = [(raw.img(int(r['pframe'])), F.load_al(os.path.join(D, N + 'r', 'f%s.rgb' % r['swap'])).resize((W, H), Image.BOX)) for r in pick]
boxes = {'inner': (3, 3, W - 3, H - 3), 'centre3d': (60, 40, W - 69, H - 17), 'radar': (W - 69, 4, W - 7, 62),
         'lives': (4, H - 47, 50, H - 2), 'icon': (4, 4, 40, 40)}
for name, b in boxes.items():
    res = {}
    for rt, al in P:
        a = al.crop(b)
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                c = rt.crop((R[0] + b[0] + dx, R[1] + b[1] + dy, R[0] + b[2] + dx, R[1] + b[3] + dy))
                res.setdefault((dx, dy), []).append(sum(ImageStat.Stat(ImageChops.difference(c, a)).mean) / 3)
    med = {k: sorted(v)[len(v) // 2] for k, v in res.items()}
    best = sorted(med, key=med.get)[:3]
    print('%-9s best %s  (0,0)=%.2f  ' % (name, ' '.join('%s=%.2f' % (k, med[k]) for k in best), med[(0, 0)]))
