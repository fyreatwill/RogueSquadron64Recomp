#!/usr/bin/env python3
# s7210: fit the presented-capture rect (and how many native rows the window shows) against a replay dir, BEFORE trusting any
# s7183_parity / s7122_fidelity model pick. TRAP (s7210): a rect off by ~4 native rows made BOB beat PROG on the 16:9 Elite Rogues
# (d 6.6); the fitted rect (rows 0-443 shown) gives d 3.0 and PROG wins 119/121. usage: s7210_regfit.py <dir> <name> <replaydir> x0,y0,x1,y1
import sys, csv, struct
from PIL import ImageChops, ImageStat
sys.path.insert(0, 'tools'); from s7122_fidelity import Raw
from PIL import Image
D, NM, GD = sys.argv[1:4]; R0 = tuple(int(v) for v in sys.argv[4].split(',')); raw = Raw('%s/%s.raw' % (D, NM))
rows = [r for r in csv.DictReader(open('%s/%sC.frames.csv' % (D, NM)))]
sel = rows[40::25][:16]
def g(s):
    d = open('%s/f%s.rgb' % (GD, s), 'rb').read(); w, h = struct.unpack('<II', d[:8]); return Image.frombytes('RGB', (w, 448), d[8:8 + w * 448 * 3])
GW = g(sel[0]['swap']).size[0]
data = [(raw.img(int(r['pframe'])), g(r['swap'])) for r in sel]
def score(rc):
    t = 0
    for P, G in data: t += sum(ImageStat.Stat(ImageChops.difference(P.crop(rc).resize((GW, 448), Image.BOX), G)).mean) / 3
    return t / len(data)
best = R0; bs = score(best)
for step in (8, 4, 2, 1):
    imp = True
    while imp:
        imp = False
        for i in range(4):
            for dv in (-step, step):
                c = list(best); c[i] += dv
                if c[3] > raw.img(0).size[1] or c[1] < 0: continue
                s = score(tuple(c))
                if s < bs: bs, best, imp = s, tuple(c), True
print('best rect', best, 'd %.3f' % bs, 'start d %.3f' % score(R0))
# second pass: also trim G rows (presented may show fewer than 448 native rows)
def score2(rc, g0, g1):
    t = 0
    for P, G in data: t += sum(ImageStat.Stat(ImageChops.difference(P.crop(rc).resize((GW, g1 - g0), Image.BOX), G.crop((0, g0, GW, g1)))).mean) / 3
    return t / len(data)
b2 = (best, 0, 448); s2 = bs
for g0 in range(0, 17, 2):
    for g1 in range(432, 449, 2):
        for y0 in range(best[1] - 8, best[1] + 9, 2):
            s = score2((best[0], y0, best[2], best[3]), g0, g1)
            if s < s2: s2, b2 = s, ((best[0], y0, best[2], best[3]), g0, g1)
print('best2', b2, 'd %.3f' % s2)
