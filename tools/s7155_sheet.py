#!/usr/bin/env python3
# s7155 owner sheet: title / SELECT GAME / SELECT LEVEL / AVAILABLE CRAFT at 16:9 (owner recipe FPS60 dd4). Columns: RT64 presented
# (RECT_ASPECT on, default) | RT64 presented RECT_ASPECT=0 | angrylion replay (n dir for title/profile, r dir for 336-row screens).
# usage: s7155_sheet.py dir out.png
import sys, csv; sys.path.insert(0, 'tools'); import s7122_fidelity as F
from PIL import Image, ImageDraw
D, O = sys.argv[1:3]; R = (0, 9, 369, 216); W, H = 369, 207
T, Q = F.Raw(D + '/T1.raw'), F.Raw(D + '/R1.raw')
ph = [('title', 'n', 900), ('prof', 'n', 1180), ('lsel', 'r', 1500), ('craft', 'r', 1800)]
sh = Image.new('RGB', (3 * W + 8, len(ph) * (H + 14) + 14)); d = ImageDraw.Draw(sh)
for j, t in enumerate(('RT64 (RECT_ASPECT on, default)', 'RT64 RECT_ASPECT=0', 'angrylion')): d.text((j * (W + 4) + 4, 2), t, fill=(255, 255, 0))
for i, (k, m, s) in enumerate(ph):
    y = 14 + i * (H + 14)
    a = min(csv.DictReader(open('%s/T1J_%s.csv' % (D, k))), key=lambda r: abs(int(r['swap']) - s))
    b = min(csv.DictReader(open('%s/R1J_%s.csv' % (D, k))), key=lambda r: abs(int(r['swap']) - s))
    sh.paste(T.img(int(a['pframe'])).crop(R).convert('RGB'), (0, y + 12))
    sh.paste(Q.img(int(b['pframe'])).crop(R).convert('RGB'), (W + 4, y + 12))
    al = F.load_al('%s/T1%s/f%s.rgb' % (D, m, a['swap']))
    if al is not None: sh.paste(al.convert('RGB').resize((W, H)), (2 * (W + 4), y + 12))
    d.text((4, y), '%s swap %s / %s' % (k, a['swap'], b['swap']), fill=(0, 255, 255))
sh.save(O); print(O)
