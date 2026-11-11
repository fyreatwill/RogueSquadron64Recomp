#!/usr/bin/env python3
"""s7153 owner sheet: OPTIONS, PASSCODES, MISSION FAILED and the mission results screen at 21:9 (owner recipe FPS60 dd4),
RT64 presented | angrylion replay of the same RDP stream; last row = ROGUESQ_RECT_ASPECT=0 arm. usage: s7153_sheet.py out.png"""
import sys, os, csv; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import s7122_fidelity as F
from PIL import Image, ImageDraw
D = 'scratch/s7153'; R = (0, 11, 469, 216); W, H = 469, 205
def pick(arm, csvn, k):
    rows = list(csv.DictReader(open('%s/%s' % (D, csvn)))); r = rows[len(rows) * k // 4]
    raw = F.Raw('%s/%s.raw' % (D, arm)); al = F.load_al('%s/%sc/f%s.rgb' % (D, arm, r['swap'])).resize((W, H), Image.BOX)
    return raw.img(int(r['pframe'])).crop(R), al, r['swap']
cells = [('OPTIONS', 'O3', 'J_O.csv', 2), ('PASSCODES', 'O3', 'J_P.csv', 2), ('MISSION FAILED (abort)', 'D3', 'DJ_F.csv', 2),
         ('mission results', 'D3', 'DJ_S.csv', 2), ('mission results, RECT_ASPECT=0', 'D4', 'EJ_S.csv', 2)]
sh = Image.new('RGB', (2 * W, len(cells) * (H + 14)), (30, 30, 30)); d = ImageDraw.Draw(sh)
for i, (lab, arm, cn, k) in enumerate(cells):
    p, a, s = pick(arm, cn, k); y = i * (H + 14)
    sh.paste(p, (0, y + 14)); sh.paste(a, (W, y + 14)); d.text((2, y + 1), '%s  swap %s   left RT64 presented | right angrylion' % (lab, s), fill=(255, 255, 0))
sh.save(sys.argv[1]); print(sys.argv[1], sh.size)
