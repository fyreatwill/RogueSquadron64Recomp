#!/usr/bin/env python3
"""s7144 owner sheet: 21:9 level select + available-craft screens, per row: RT64 fix on | angrylion (same stream) | RT64 ROGUESQ_RECT_ASPECT=0.
usage: s7144_sheet.py dir out.png onswap:offswap [...]   (dir holds M1/M2 raw + replays + frames.csv; rect 0,11,469,216)"""
import sys, os, csv, importlib.util
sp = importlib.util.spec_from_file_location('f', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py')); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
from PIL import Image, ImageDraw
D, out, pairs = sys.argv[1], sys.argv[2], [p.split(':') for p in sys.argv[3:]]
rect = (0, 11, 469, 216); W, H = 469, 205; Z = 2
def pres(n, sw):
    r = {x['swap']: x for x in csv.DictReader(open(f'{D}/{n}.frames.csv'))}[sw]; return F.Raw(f'{D}/{n}.raw').img(int(r['pframe'])).crop(rect)
S = Image.new('RGB', (3 * W * Z, len(pairs) * (H * Z + 16)), (30, 30, 30)); d = ImageDraw.Draw(S)
for i, (a, b) in enumerate(pairs):
    ims = [pres('M1', a), F.load_al(f'{D}/M1r/f{a}.rgb').resize((W, H), Image.BOX), pres('M2', b)]
    for j, (im, lab) in enumerate(zip(ims, ['RT64 (fix on, default)', 'angrylion (accurate N64 model)', 'RT64 RECT_ASPECT=0 (old)'])):
        S.paste(im.resize((W * Z, H * Z), Image.LANCZOS), (j * W * Z, i * (H * Z + 16) + 16)); d.text((j * W * Z + 6, i * (H * Z + 16) + 2), lab, fill=(255, 255, 255))
S.save(out, optimize=True); print(out, S.size)
