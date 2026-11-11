#!/usr/bin/env python3
"""s7150: owner sheet for the in-flight pause menu: RT64 presented (P3 -> sRGB) vs angrylion replay of the same swap, 21:9 and 4:3.
usage: s7150_pause_sheet.py out.png   (reads scratch/s7150 P1 / Q4 raws, replays and pause pframe joins)"""
import os, sys, csv, importlib.util
from PIL import Image, ImageDraw
os.environ['FID_P3'] = '1'
sp = importlib.util.spec_from_file_location('f', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py')); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
D = 'scratch/s7150'; tiles = []
for N, R, lab in (('P1', (0, 11, 469, 216), '21:9'), ('Q4', (0, 8, 307, 240), '4:3')):
    raw = F.Raw(f'{D}/{N}.raw'); r = list(csv.DictReader(open(f'{D}/{N}F_pause_pf.csv')))[40]; p = int(r['pframe']) + int(r['off'])
    W, H = R[2] - R[0], R[3] - R[1]; s = 700 / W
    rt = raw.img(p).crop(R).resize((700, int(H * s)), Image.LANCZOS); al = F.load_al(f"{D}/{N}f/f{r['swap']}.rgb").resize((700, int(H * s)), Image.LANCZOS)
    tiles.append((f'{lab} RT64 presented (swap {r["swap"]})', rt)); tiles.append((f'{lab} angrylion, same RDP stream', al))
Wt = 1420; Ht = sum(t[1].height for t in tiles[::2]) + 40 * 2 + 10
out = Image.new('RGB', (Wt, Ht), (20, 20, 20)); d = ImageDraw.Draw(out); y = 0
for i in range(0, 4, 2):
    for j in range(2):
        lab, im = tiles[i + j]; d.text((10 + j * 710, y + 12), lab, fill=(255, 255, 255)); out.paste(im, (10 + j * 710, y + 34))
    y += tiles[i][1].height + 40
out.save(sys.argv[1]); print('wrote', sys.argv[1], out.size)
