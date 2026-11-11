#!/usr/bin/env python3
"""s7143: sub-pixel x/y registration sweep (angrylion side shifted in 1/4 compare px) per box, to tell a text-only (rect) shift from a
whole-frame capture offset.  usage: s7143_subpix.py raw aldir frames.csv rect "name=x0:y0:x1:y1;..." [nsample]"""
import sys, os, csv, statistics as S, importlib.util
sp = importlib.util.spec_from_file_location('f', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py')); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
from PIL import Image
raw = F.Raw(sys.argv[1]); ald = sys.argv[2]
rows = [r for r in csv.DictReader(open(sys.argv[3])) if int(r['pframe']) > 0]
R = tuple(map(int, sys.argv[4].split(','))); boxes = [(b.split('=')[0], tuple(map(int, b.split('=')[1].split(':')))) for b in sys.argv[5].split(';')]
n = int(sys.argv[6]) if len(sys.argv) > 6 else 30; rows = rows[::max(1, len(rows) // n)][:n]; W, H = R[2] - R[0], R[3] - R[1]
Q = 4; shifts = [(sx, sy) for sx in range(-4, 5) for sy in (-2, 0, 2, 4, 6)]
res = {}
for r in rows:
    al = F.load_al(os.path.join(ald, 'f%s.rgb' % r['swap']))
    if al is None: continue
    a4 = al.resize((W * Q, H * Q), Image.BOX); p = raw.img(int(r['pframe'])).crop(R)
    for sx, sy in shifts:
        a = a4.transform(a4.size, Image.AFFINE, (1, 0, -sx, 0, 1, -sy), Image.NEAREST).resize((W, H), Image.BOX)
        for nm, b in boxes:
            d = F.dmap(a.crop(b), p.crop(b)); res.setdefault(nm, {}).setdefault((sx, sy), []).append(sum(v > F.T for v in d) / len(d))
print('frames', len(rows), '(shift = angrylion content moved by sx/4, sy/4 compare px; + = right/down)')
for nm, b in boxes:
    t = {k: S.median(v) for k, v in res[nm].items()}
    for sy in (-2, 0, 2, 4, 6): print("  %-8s sy=%+d: %s" % (nm, sy, " ".join("%.3f" % t[(sx, sy)] for sx in range(-4, 5))))
for nm, b in boxes:
    t = {k: S.median(v) for k, v in res[nm].items()}; best = min(t, key=t.get)
    print('%-8s %s base %.4f best %s %.4f | x row(sy=0): %s' % (nm, b, t[(0, 0)], best, t[best], ' '.join('%.3f' % t[(sx, 0)] for sx in range(-4, 5))))
