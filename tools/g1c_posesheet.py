#!/usr/bin/env python3
"""Arm-vs-arm contact sheet from ROGUESQ_FB_DUMP_EVERY dumps.
Usage: g1c_posesheet.py out.png armdir:fbn[,fbn..] ...   (one column per arm, one row per fbn)
fbn = the fbdump n for that arm (pick via [poselock] n= lines in run.log). Prints per-row mean diff vs column 0.
NOTE: poselock pins position only; camera attitude still varies, so rows are not guaranteed view-matched."""
import sys, glob
from PIL import Image, ImageDraw, ImageChops, ImageStat
W, H = 320, 240
cols = [a.split(':') for a in sys.argv[2:]]
nrows = max(len(c[1].split(',')) for c in cols)
im = Image.new('RGB', (W*len(cols), H*nrows)); d = ImageDraw.Draw(im)
fr = {}
for ci, (dr, ns) in enumerate(cols):
    for ri, n in enumerate(ns.split(',')):
        f = Image.open(glob.glob(f'{dr}/fbd/fb_{int(n):07d}_w*.ppm')[0]).convert('RGB').resize((W, H))
        fr[(ci, ri)] = f; im.paste(f, (ci*W, ri*H)); d.text((ci*W+4, ri*H+4), f'{dr.split("/")[-1]} {n}', fill=(255, 255, 0))
im.save(sys.argv[1])
for (ci, ri), f in fr.items():
    if ci and (0, ri) in fr:
        print(ri, ci, round(sum(ImageStat.Stat(ImageChops.difference(fr[(0, ri)], f)).mean)/3, 2))
