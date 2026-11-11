#!/usr/bin/env python3
"""s7147: joint (x-scale k, y-scale e, y offset sy, x offset sx) fit of angrylion onto the RT64 presented crop, per box.
Tests H-ycouple: on the perspective crawl a y-mapping error moves glyph x in opposite directions on the left and right (the trapezoid
shears), which a fixed-e x-scale sweep reads as an x-scale. If the joint best k returns to 1.000 once (e, sy) are free, the s7146 1.0025
x-scale was y coupling, not an x presentation term.
usage: s7147_joint_fit.py raw aldir frames.csv "name=x0:y0:x1:y1;..." [nsample]   env: JK JE JY JX (comma grids; sx, sy in 1/4 px)"""
import sys, os, csv, statistics as S, importlib.util, itertools
sp = importlib.util.spec_from_file_location('f', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py')); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
from PIL import Image
raw = F.Raw(sys.argv[1]); ald = sys.argv[2]; R = (0, 11, 469, 216); W, H = 469, 205; Q = 4; cx = W / 2 * Q
rows = [r for r in csv.DictReader(open(sys.argv[3])) if int(r['pframe']) > 0]
n = int(sys.argv[5]) if len(sys.argv) > 5 else 16; rows = rows[::max(1, len(rows) // n)][:n]
boxes = [(b.split('=')[0], tuple(map(int, b.split('=')[1].split(':')))) for b in sys.argv[4].split(';')]
fr = []
for r in rows:
    al = F.load_al(os.path.join(ald, 'f%s.rgb' % r['swap']))
    if al is not None: fr.append((al.resize((W * Q, H * Q), Image.BOX), raw.img(int(r['pframe'])).crop(R)))
g = lambda k, d: tuple(map(float, os.environ.get(k, d).split(',')))
GK, GE, GY, GX = g('JK', '0.995,0.9975,1.0,1.0025,1.005'), g('JE', '0.984,0.988,0.992,0.996,1.0'), g('JY', '-2,0,2'), g('JX', '0,1,2')
def warp(a4, k, e, sx, sy): return a4.transform(a4.size, Image.AFFINE, (k, 0, -sx + cx * (1 - k), 0, e, -sy), Image.BILINEAR).resize((W, H), Image.BOX)
def frac(a, p, b): d = F.dmap(a.crop(b), p.crop(b)); return sum(v > F.T for v in d) / len(d)
print('frames', len(fr))
tab = {}
for k, e, sx, sy in itertools.product(GK, GE, GX, GY):
    ws = [(warp(a, k, e, sx, sy), p) for a, p in fr]
    tab[(k, e, sx, sy)] = {nm: S.median(frac(w, p, b) for w, p in ws) for nm, b in boxes}
for nm, _ in boxes:
    best = min(tab, key=lambda t: tab[t][nm])
    perk = {k: min(v[nm] for t, v in tab.items() if t[0] == k) for k in GK}
    print('%-7s best (k,e,sx,sy)=%s %.4f | min over (e,sx,sy) per k: %s' % (nm, best, tab[best][nm], ' '.join('%.4f:%.4f' % (k, perk[k]) for k in GK)))
