#!/usr/bin/env python3
"""s7152 owner sheet: title (START/OPTIONS) and SELECT GAME at 21:9, RT64 presented | angrylion, plus level select fix on vs
ROGUESQ_RECT_ASPECT=0 (the same-iteration positive control). usage: s7152_sheet.py out.png"""
import sys, os, csv; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import s7122_fidelity as F
from PIL import Image, ImageDraw
D = 'scratch/s7152'; R = (0, 11, 469, 216); W, H = 469, 205
def pick(arm, csvn, k):
    rows = list(csv.DictReader(open('%s/%s' % (D, csvn)))); r = rows[len(rows) * k // 4]
    raw = F.Raw('%s/%s.raw' % (D, arm)); al = F.load_al('%s/%sc/f%s.rgb' % (D, arm, r['swap'])).resize((W, H), Image.BOX)
    return raw.img(int(r['pframe'])).crop(R), al, r['swap']
cells = [('title, RECT_ASPECT on', 'M1', 'C1_T.csv', 2), ('SELECT GAME, on', 'M1', 'C1_S.csv', 2),
         ('SELECT GAME, RECT_ASPECT=0', 'R0', 'R0C_S.csv', 2), ('level select, on', 'M1', 'C1_L.csv', 1),
         ('level select, RECT_ASPECT=0 (control)', 'R0', 'R0C_L.csv', 1)]
sh = Image.new('RGB', (2 * W, len(cells) * (H + 14)), (30, 30, 30)); d = ImageDraw.Draw(sh)
for i, (lab, arm, cn, k) in enumerate(cells):
    p, a, s = pick(arm, cn, k); y = i * (H + 14)
    sh.paste(p, (0, y + 14)); sh.paste(a, (W, y + 14)); d.text((2, y + 1), '%s  swap %s   left RT64 presented | right angrylion' % (lab, s), fill=(255, 255, 0))
sh.save(sys.argv[1]); print(sys.argv[1], sh.size)
