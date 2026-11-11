#!/usr/bin/env python3
"""s7141: centre (4:3 band) vs side-band frac>40 with the edge-anchored HUD boxes masked out, over a sample of a frames.csv.
usage: s7141_mask.py raw aldir frames.csv rect cx0,cx1 "x0:y0:x1:y1;..." [nsample]   (mask boxes in compare coords)"""
import sys, os, csv, statistics as S, importlib.util
sp = importlib.util.spec_from_file_location('f', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py')); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
from PIL import Image
raw = F.Raw(sys.argv[1]); ald = sys.argv[2]; rows = [r for r in csv.DictReader(open(sys.argv[3])) if int(r['pframe']) > 0]
R = tuple(map(int, sys.argv[4].split(','))); c0, c1 = map(int, sys.argv[5].split(','))
boxes = [tuple(map(int, b.split(':'))) for b in sys.argv[6].split(';') if b]; n = int(sys.argv[7]) if len(sys.argv) > 7 else 120
rows = rows[::max(1, len(rows) // n)][:n]; W, H = R[2] - R[0], R[3] - R[1]
cls = bytearray(W * H)  # 0 centre, 1 side, 2 masked
for y in range(H):
    for x in range(W):
        cls[y * W + x] = 2 if any(b[0] <= x < b[2] and b[1] <= y < b[3] for b in boxes) else (0 if c0 <= x < c1 else 1)
fc, fs, hud = [], [], []
for r in rows:
    a = F.load_al(os.path.join(ald, 'f%s.rgb' % r['swap'])).resize((W, H), Image.BOX); p = raw.img(int(r['pframe'])).crop(R)
    d = F.dmap(a, p); t = [[0, 0], [0, 0], [0, 0]]
    for i, v in enumerate(d): k = cls[i]; t[k][0] += v > F.T; t[k][1] += 1
    fc.append(t[0][0] / t[0][1]); fs.append(t[1][0] / t[1][1]); hud.append(t[2][0] / max(1, t[2][1]))
print('frames', len(rows), 'centre frac med %.4f p90 %.4f | side (HUD masked) med %.4f p90 %.4f | HUD boxes med %.4f' % (
    S.median(fc), sorted(fc)[int(.9 * len(fc))], S.median(fs), sorted(fs)[int(.9 * len(fs))], S.median(hud)))
