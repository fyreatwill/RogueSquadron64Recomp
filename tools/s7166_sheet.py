#!/usr/bin/env python3
"""s7166: before/after owner sheet for the L4 21:9 cutscene hole. Rows = arms, columns = angrylion replay of the swap and the RT64
presented frame nearest that swap's mach time (+10 ms lag). usage: s7166_sheet.py out.png "label:dir/name:swap" ...
(dir/name -> <dir>/<name>r/f<swap>.rgb, <dir>/<name>.raw, <dir>/<name>.idx; rect 1,11,469,216 of the 504x216 capture)."""
import importlib.util, os, sys
from PIL import Image, ImageDraw
spec = importlib.util.spec_from_file_location('F', os.path.join(os.path.dirname(__file__), 's7122_fidelity.py'))
F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
def al(p):
    b = open(p, 'rb').read(); w = int.from_bytes(b[:4], 'little'); h = int.from_bytes(b[4:8], 'little')
    return Image.frombytes('RGB', (w, h), b[8:8 + 3 * w * h])
rows = []
for a in sys.argv[2:]:
    lab, dn, sw = a.split(':'); d, n = os.path.split(dn); sw = int(sw)
    A = al(os.path.join(d, n + 'r', 'f%d.rgb' % sw)).crop((0, 54, 1024, 394)).resize((468, 155))
    m = {int(l.split()[0]): int(l.split()[1]) for l in open(os.path.join(d, n + '.idx'))}
    raw = F.Raw(os.path.join(d, n + '.raw')); t = m[sw] + 240000; i = min(range(len(raw.T)), key=lambda k: abs(raw.T[k] - t))
    R = raw.img(i).crop((1, 11, 469, 216)).convert('RGB').resize((468, 205))
    rows.append((lab + ' swap %d' % sw, A, R))
S = Image.new('RGB', (2 * 476, len(rows) * 232 + 4), (40, 40, 40)); D = ImageDraw.Draw(S)
for k, (lab, A, R) in enumerate(rows):
    y = 4 + k * 232; S.paste(A, (4, y + 18 + 25)); S.paste(R, (480, y + 18)); D.text((6, y + 2), lab + '   left: angrylion replay (magenta = never drawn)   right: RT64 presented', fill=(255, 255, 255))
S.save(sys.argv[1]); print('wrote', sys.argv[1])
