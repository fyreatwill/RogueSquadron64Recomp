#!/usr/bin/env python3
"""s7148: owner sheet, mission intro cutscene at 16:9, RT64 presented | angrylion (same RDP stream) per row, with the swap number.
usage: s7148_sheet.py raw aldir pf.csv[,pf.csv...] rect swaps(comma) out.png"""
import sys, os, csv, importlib.util
sp = importlib.util.spec_from_file_location('f', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py')); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
from PIL import Image, ImageDraw
raw = F.Raw(sys.argv[1]); ald = sys.argv[2]; R = tuple(map(int, sys.argv[4].split(','))); W, H = R[2] - R[0], R[3] - R[1]
pf = {}
for p in sys.argv[3].split(','):
    for x in csv.DictReader(open(p)): pf[x['swap']] = int(x['pframe']) + int(x['off'])
sw = sys.argv[5].split(','); Z = 2; S = Image.new('RGB', (2 * W * Z + 10, (H * Z + 20) * len(sw)), (40, 40, 40)); d = ImageDraw.Draw(S)
for i, s in enumerate(sw):
    y = i * (H * Z + 20); p = raw.img(pf[s]).crop(R).resize((W * Z, H * Z), Image.LANCZOS)
    a = F.load_al(os.path.join(ald, 'f%s.rgb' % s)).resize((W * Z, H * Z), Image.LANCZOS)
    S.paste(p, (0, y + 18)); S.paste(a, (W * Z + 10, y + 18))
    d.text((4, y + 3), 'swap %s  RT64 (port, presented window)' % s, fill=(255, 255, 0)); d.text((W * Z + 14, y + 3), 'angrylion (accurate N64 model, same stream)', fill=(255, 255, 0))
S.save(sys.argv[6]); print(sys.argv[6], S.size)
