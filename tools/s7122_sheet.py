#!/usr/bin/env python3
"""s7122 owner sheet: angrylion | RT64 presented | diff mask (pixels over T in red) for the N worst frames by frac_over_T.
usage: s7122_sheet.py raw idx aldir prefix x0,y0,x1,y1 out.png [N=4] [label]"""
import sys, csv, os
sys.path.insert(0, os.path.dirname(__file__))
from s7122_fidelity import Raw, load_al, dmap, T
from PIL import Image, ImageDraw
raw, idx, aldir, pre, rect, out = sys.argv[1:7]; N = int(sys.argv[7]) if len(sys.argv) > 7 else 4; lab = sys.argv[8] if len(sys.argv) > 8 else ''
rect = tuple(map(int, rect.split(','))); size = (rect[2] - rect[0], rect[3] - rect[1]); W, H = size
R = sorted(csv.DictReader(open(pre + '.frames.csv')), key=lambda r: -float(r['frac_over_T']))[:N]
rw = Raw(raw); S = 2; sheet = Image.new('RGB', (3 * W * S, N * (H * S + 14)), (20, 20, 20)); dr = ImageDraw.Draw(sheet)
for k, r in enumerate(R):
    a = load_al(os.path.join(aldir, 'f%s.rgb' % r['swap'])).resize(size, Image.BOX); p = rw.img(int(r['pframe'])).crop(rect)
    d = dmap(a, p); m = Image.frombytes('L', size, bytes(255 if v > T else min(255, v * 3) // 3 for v in d))
    red = Image.merge('RGB', (m.point(lambda v: 255 if v == 255 else v), m.point(lambda v: 0 if v == 255 else v), m.point(lambda v: 0 if v == 255 else v)))
    y = k * (H * S + 14)
    for j, im in enumerate((a, p, red)): sheet.paste(im.resize((W * S, H * S), Image.NEAREST), (j * W * S, y + 14))
    dr.text((4, y + 1), '%s swap %s  angrylion | RT64 presented | diff (red > %d)  mean|d| %s  frac %s' % (lab, r['swap'], T, r['meand'], r['frac_over_T']), fill=(255, 255, 255))
sheet.save(out); print(out, sheet.size)
