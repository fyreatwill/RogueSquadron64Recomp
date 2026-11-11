#!/usr/bin/env python3
"""s7156 (from s7146_sheet): owner sheet, logo + opening text crawl at any aspect (env SHEET_RECT, SHEET_LABEL): RT64 presented | angrylion replay, per row.
usage: s7145_sheet.py raw aldir frames.csv out.png swap1,swap2,..."""
import sys, os, csv, importlib.util
sp = importlib.util.spec_from_file_location('f', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py')); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
from PIL import Image, ImageDraw
raw = F.Raw(sys.argv[1]); rows = {r['swap']: r for r in csv.DictReader(open(sys.argv[3]))}; R = tuple(map(int, os.environ.get('SHEET_RECT', '0,11,469,216').split(','))); W, H = R[2] - R[0], R[3] - R[1]; L = os.environ.get('SHEET_LABEL', '21:9')
sw = sys.argv[5].split(','); S = Image.new('RGB', (2 * W + 6, len(sw) * (H + 16)), (40, 40, 40)); d = ImageDraw.Draw(S)
for i, s in enumerate(sw):
    r = rows[s]; y = i * (H + 16)
    S.paste(raw.img(int(r['pframe'])).crop(R), (0, y + 14)); S.paste(F.load_al(os.path.join(sys.argv[2], 'f%s.rgb' % s)).resize((W, H), Image.BOX), (W + 6, y + 14))
    d.text((4, y + 1), 'RT64 %s swap %s (frac_c %s)' % (L, s, r['frac_c']), fill=(255, 255, 0)); d.text((W + 10, y + 1), 'angrylion', fill=(255, 255, 0))
S.save(sys.argv[4]); print(sys.argv[4], S.size)
