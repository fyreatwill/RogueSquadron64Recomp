#!/usr/bin/env python3
"""s7141: column profile of RT64-vs-angrylion |d| and a rect-registration sweep, using the pairings in a s7122 frames.csv.
usage: s7141_colprof.py raw aldir frames.csv rect x0,y0,x1,y1 [nsample=40]
Prints mean d per 1/16 width column bucket for the given rect, then the median mean|d| over the sample for rects with x0/x1 varied
by -2..+2 (a registration/scale error shows as a lower score off the nominal rect and as diff growing toward the edges)."""
import sys, os, csv, statistics as S
sys.path.insert(0, os.path.dirname(__file__))
import importlib.util
sp = importlib.util.spec_from_file_location('f', os.path.join(os.path.dirname(__file__), 's7122_fidelity.py')); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
from PIL import Image
raw = F.Raw(sys.argv[1]); ald = sys.argv[2]; rows = [r for r in csv.DictReader(open(sys.argv[3])) if int(r['pframe']) > 0]
R = tuple(map(int, sys.argv[4].split(','))); n = int(sys.argv[5]) if len(sys.argv) > 5 else 40
rows = rows[::max(1, len(rows) // n)][:n]
pairs = [(F.load_al(os.path.join(ald, 'f%s.rgb' % r['swap'])), raw.img(int(r['pframe']))) for r in rows]
def score(rect, prof=False):
    W, H = rect[2] - rect[0], rect[3] - rect[1]; out = []; col = [0.0] * 16
    for a, p in pairs:
        d = F.dmap(a.resize((W, H), Image.BOX), p.crop(rect)); out.append(sum(d) / len(d))
        if prof:
            for y in range(H):
                for x in range(W): col[x * 16 // W] += d[y * W + x]
    if prof:
        per = W * H / 16 * len(pairs); print('col profile (16 buckets):', ' '.join('%.1f' % (c / per) for c in col))
    return S.median(out)
print('nominal', R, '%.2f' % score(R, True))
for dx0 in (-2, -1, 0, 1, 2):
    print('x0%+d:' % dx0, ' '.join('x1%+d=%.2f' % (dx1, score((R[0] + dx0, R[1], R[2] + dx1, R[3]))) for dx1 in (-2, -1, 0, 1, 2)))
for dy0, dy1 in ((-1, 0), (1, 0), (0, -1), (0, 1)):
    print('y0%+d y1%+d: %.2f' % (dy0, dy1, score((R[0], R[1] + dy0, R[2], R[3] + dy1))))
