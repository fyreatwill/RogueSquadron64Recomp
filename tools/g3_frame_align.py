#!/usr/bin/env python3
"""s6873 G3: is a same-pose residual a whole-view camera offset? Finds the integer (dx, dy) that best aligns ARM to BASE per freeze k,
in three screen bands of the game area (sky, craft row, ground), and scores MAD before and after. A residual that drops to the
floor under one shift for every band = camera translation or a stale presented frame; bands disagreeing = rotation or parallax.
Usage: g3_frame_align.py ARMS_DIR BASE ARM [ARM ...]"""
import os, sys
from PIL import Image, ImageChops, ImageStat
R = 12

def load(root, arm, k):
    p = os.path.join(root, arm, 'f%d_1.png' % k)
    if not os.path.exists(p):
        return None
    a = Image.open(p).convert('L')
    w, h = a.size
    return a.crop((int(w * .08), int(h * .08), int(w * .92), int(h * .98)))

def mad(b, m, box, dx=0, dy=0):
    x0, y0, x1, y1 = box
    return ImageStat.Stat(ImageChops.difference(b.crop(box), m.crop((x0 + dx, y0 + dy, x1 + dx, y1 + dy)))).mean[0]

def best(b, m, box):
    return min((mad(b, m, box, dx, dy), dx, dy) for dy in range(-R, R + 1) for dx in range(-R, R + 1))

def main():
    root, base, arms = sys.argv[1], sys.argv[2], sys.argv[3:]
    print('%-6s %1s %-5s %7s %7s %4s %4s' % ('arm', 'k', 'band', 'mad0', 'best', 'dx', 'dy'))
    for n in arms:
        for k in range(3):
            b, m = load(root, base, k), load(root, n, k)
            if b is None or m is None or b.size != m.size:
                continue
            w, h = b.size
            for name, y0, y1 in (('sky', R, h // 3), ('craft', h // 3, 2 * h // 3), ('gnd', 2 * h // 3, h - R)):
                box = (R, y0, w - R, y1)
                r = best(b, m, box)
                print('%-6s %d %-5s %7.2f %7.2f %4d %4d' % (n, k, name, mad(b, m, box), r[0], r[1], r[2]))

main()
