#!/usr/bin/env python3
"""s7310 G5f: count near-white (all channels >235) pixels in the left and right 1% columns of window captures (rows below the
56 px title bar). usage: s7310_sliver_score.py png..."""
import sys
from PIL import Image
for f in sys.argv[1:]:
    im = Image.open(f).convert('RGB'); w, h = im.size; c = max(2, w // 100); px = im.load()
    cnt = lambda xs: sum(1 for y in range(56, h) for x in xs if min(px[x, y]) > 235)
    print(f, w, h, 'left', cnt(range(c)), 'right', cnt(range(w - c, w)))
