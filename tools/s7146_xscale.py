#!/usr/bin/env python3
"""s7146 (from scratch/s7145/xscale.py): x-scale sweep about the screen centre at a fixed registration, per box.
A wide-path x stretch shows as a minimum away from 1.000 and as left/right boxes wanting opposite x offsets.
usage: s7146_xscale.py raw aldir frames.csv sx sy e "name=x0:y0:x1:y1;..." [nsample]   (sx, sy in 1/4 compare px, as s7143_affine)"""
import sys, os, csv, statistics as S, importlib.util
sp = importlib.util.spec_from_file_location('f', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py')); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
from PIL import Image
raw = F.Raw(sys.argv[1]); ald = sys.argv[2]; R = (0, 11, 469, 216); W, H = 469, 205; Q = 4
rows = [r for r in csv.DictReader(open(sys.argv[3])) if int(r['pframe']) > 0]
n = int(sys.argv[8]) if len(sys.argv) > 8 else 24; rows = rows[::max(1, len(rows) // n)][:n]
sx, sy, e = float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]); cx = W / 2 * Q
boxes = [(b.split('=')[0], tuple(map(int, b.split('=')[1].split(':')))) for b in sys.argv[7].split(';')]
fr = []
for r in rows:
    al = F.load_al(os.path.join(ald, 'f%s.rgb' % r['swap']))
    if al is not None: fr.append((al.resize((W * Q, H * Q), Image.BOX), raw.img(int(r['pframe'])).crop(R)))
def warp(a4, k, dx=0): return a4.transform(a4.size, Image.AFFINE, (k, 0, -(sx + dx) + cx * (1 - k), 0, e, -sy), Image.BILINEAR).resize((W, H), Image.BOX)
def frac(a, p, b): d = F.dmap(a.crop(b), p.crop(b)); return sum(v > F.T for v in d) / len(d)
print('frames', len(fr))
for k in tuple(map(float, os.environ.get("XS_K", "0.98,0.99,0.995,1.0,1.005,1.01,1.02").split(","))):
    print('xscale %.3f ' % k + ' '.join('%s %.4f' % (nm, S.median(frac(warp(a, k), p, b) for a, p in fr)) for nm, b in boxes))
for dx in (-2, -1, 0, 1, 2):
    print('dx %+d/4 px ' % dx + ' '.join('%s %.4f' % (nm, S.median(frac(warp(a, 1.0, dx), p, b) for a, p in fr)) for nm, b in boxes))
