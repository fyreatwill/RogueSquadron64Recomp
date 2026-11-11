#!/usr/bin/env python3
"""s7129 wsheet-escape owner sheet. Row 0: the s7125 visible escaper (before the W_SHEET_POS cull, crop of the s7125 sheet).
Rows 1..: W_SHEET_POS fires from the s7128 trigger-ring captures: angrylion (hardware) | RT64 presented, wedge corner->base path
marked in cyan (dropped arm, cull on) or yellow (kept arm, wedge drawn). Equal pixels along the mark = nothing visible lost/shown.
usage: s7129_sheet.py out.png s7125_sheet.png  run:swap:posline ...   (run = scratch/s7128/<run>, posline = 0-based line of <run>_drop.txt.pos)"""
import sys, os, bisect
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location('fid', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py'))
fid = importlib.util.module_from_spec(spec); spec.loader.exec_module(fid)
RECT = (0, 9, 369, 216); LAG = 25 * 24000; CW, CH = 728, 408
out, before = sys.argv[1], sys.argv[2]; rows = []
b = Image.open(before); bw, bh = b.size; rh = bh // 4
top = b.crop((0, 0, bw * 2 // 3, rh)); top = top.resize((CW * 2, int(top.size[1] * CW * 2 / top.size[0])))
rows.append(('BEFORE (s7125 n1, no cull): angrylion | RT64 - the dark band is the escaped corner wedge', top))
for spec_ in sys.argv[3:]:
    run, swap, li = spec_.split(':'); swap = int(swap); d = 'scratch/s7128'
    raw = fid.Raw(f'{d}/{run}.raw'); sw = {int(l.split()[0]): int(l.split()[1]) for l in open(f'{d}/{run}.idx')}
    p = open(f'{d}/{run}_drop.txt.pos').read().split('\n')[int(li)].split(); arm = int(p[10])
    v = [(float(p[1]), float(p[2])), (float(p[3]), float(p[4])), (float(p[5]), float(p[6]))]
    a = fid.load_al(f'{d}/{run}r/f{swap}.rgb'); aw, ah = a.size; W, H = RECT[2] - RECT[0], RECT[3] - RECT[1]
    a_s = a.resize((W, H), Image.BOX); i0 = min(bisect.bisect_left(raw.T, sw[swap] + LAG), len(raw.T) - 1)
    best = min((sum(fid.dmap(a_s, raw.img(j).crop(RECT))) , j) for j in range(max(0, i0 - 2), min(len(raw.T), i0 + 3)))
    pr = raw.img(best[1]).crop(RECT)
    col = (0, 255, 255) if arm else (255, 230, 0)
    ims = []
    for im in (a, pr):
        im = im.resize((CW, CH), Image.LANCZOS); dr = ImageDraw.Draw(im); sx, sy = CW / aw, CH / ah
        q = [(x * sx, y * sy) for x, y in v]
        dr.line(q + [q[0]], fill=col, width=1)
        # tick marks either side so the path is visible without covering it
        for (x, y) in q:
            if 0 <= x < CW and 0 <= y < CH: dr.ellipse((x - 5, y - 5, x + 5, y + 5), outline=col)
        ims.append(im)
    r = Image.new('RGB', (CW * 2, CH)); r.paste(ims[0], (0, 0)); r.paste(ims[1], (CW, 0))
    rows.append((f'{run} swap {swap}: {"DROPPED by cull (cyan)" if arm else "KEPT control (yellow)"} W={p[7]} | angrylion | RT64 presented', r))
H = sum(im.size[1] + 18 for _, im in rows); S = Image.new('RGB', (CW * 2, H), (16, 16, 16)); dr = ImageDraw.Draw(S); y = 0
for t, im in rows:
    dr.text((4, y + 3), t, fill=(230, 230, 230)); S.paste(im, (0, y + 18)); y += im.size[1] + 18
S.save(out); print(out, S.size)
