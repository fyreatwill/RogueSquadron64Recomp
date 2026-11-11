#!/usr/bin/env python3
"""s7141 owner sheet: rows of angrylion | RT64 presented | diff x4 for chosen swaps. usage: s7141_sheet.py out.png raw:aldir:frames.csv:x0,y0,x1,y1:swap,swap,..  [...]"""
import sys, os, csv, importlib.util
sp = importlib.util.spec_from_file_location('f', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py')); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
from PIL import Image, ImageDraw
rows = []
for spec in sys.argv[2:]:
    rawp, ald, fr, rect, sws = spec.split(':'); R = tuple(map(int, rect.split(','))); raw = F.Raw(rawp)
    pf = {r['swap']: r for r in csv.DictReader(open(fr))}; W, H = R[2] - R[0], R[3] - R[1]
    for s in sws.split(','):
        a = F.load_al(os.path.join(ald, 'f%s.rgb' % s)).resize((W, H), Image.BOX); p = raw.img(int(pf[s]['pframe'])).crop(R)
        d = F.dmap(a, p); dm = Image.frombytes('L', (W, H), bytes(min(255, v * 4) for v in d)).convert('RGB')
        rows.append(('%s swap %s frac>40 %s' % (os.path.basename(rawp), s, pf[s]['frac_over_T']), (a, p, dm)))
W = max(r[1][0].size[0] for r in rows); H = max(r[1][0].size[1] for r in rows)
sh = Image.new('RGB', (3 * W, len(rows) * (H + 14)), (0, 0, 0)); g = ImageDraw.Draw(sh)
for k, (lab, ims) in enumerate(rows):
    for i, im in enumerate(ims): sh.paste(im, (i * W, k * (H + 14) + 14))
    g.text((4, k * (H + 14) + 1), lab + '   [angrylion | RT64 | diff x4]', fill=(255, 255, 0))
sh.save(sys.argv[1]); print('wrote', sys.argv[1], len(rows), 'rows')
