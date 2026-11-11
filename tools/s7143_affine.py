#!/usr/bin/env python3
"""s7143: fit ONE global sub-pixel affine registration (x offset, y offset, y scale) of angrylion onto the RT64 presented crop using the 3D
centre band WITHOUT the title box, then score each box at nominal vs the fitted registration.  If text boxes drop to the 3D floor under a
registration fitted on non-text pixels, the residual is capture geometry, not RT64 text drawing.
usage: s7143_affine.py raw aldir frames.csv rect fitbox "name=x0:y0:x1:y1;..." [nsample]"""
import sys, os, csv, statistics as S, importlib.util
sp = importlib.util.spec_from_file_location('f', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py')); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
from PIL import Image
raw = F.Raw(sys.argv[1]); ald = sys.argv[2]
rows = [r for r in csv.DictReader(open(sys.argv[3])) if int(r['pframe']) > 0]
R = tuple(map(int, sys.argv[4].split(','))); FB = tuple(map(int, sys.argv[5].split(':')))
boxes = [(b.split('=')[0], tuple(map(int, b.split('=')[1].split(':')))) for b in sys.argv[6].split(';')]
n = int(sys.argv[7]) if len(sys.argv) > 7 else 24; rows = rows[::max(1, len(rows) // n)][:n]; W, H = R[2] - R[0], R[3] - R[1]; Q = 4
fr = []
for r in rows:
    al = F.load_al(os.path.join(ald, 'f%s.rgb' % r['swap']))
    if al is not None: fr.append((al.resize((W * Q, H * Q), Image.BOX), raw.img(int(r['pframe'])).crop(R)))
def warp(a4, sx, sy, e): return a4.transform(a4.size, Image.AFFINE, (1, 0, -sx, 0, e, -sy), Image.BILINEAR).resize((W, H), Image.BOX)
def frac(a, p, b): d = F.dmap(a.crop(b), p.crop(b)); return sum(v > F.T for v in d) / len(d)
def med(sx, sy, e, b, sub=fr): return S.median(frac(warp(a4, sx, sy, e), p, b) for a4, p in sub)
grid = [(sx, sy, e) for sx in (1, 2, 3, 4) for sy in (-2, 0, 2, 4) for e in (1.0, 0.996, 0.992, 0.988, 0.984)]
sub = fr[::3]; t = {g: med(*g, FB, sub) for g in grid}; g0 = min(t, key=t.get)
print('frames', len(fr), 'fit on', FB, 'nominal %.4f' % med(0, 0, 1.0, FB), 'best (sx/4, sy/4, yscale) =', g0, '%.4f (fit subset)' % t[g0])
for nm, b in boxes:
    print('%-10s %-20s nominal %.4f  fitted %.4f' % (nm, b, med(0, 0, 1.0, b), med(*g0, b)))
