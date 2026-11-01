#!/usr/bin/env python3
"""Letterbox/pillarbox score for G1f window captures (s6717).

Usage: g1f_bar_score.py <png> [<png> ...]
Per image: size, aspect, and the width of the black bars at each edge -- the
count of whole columns (left/right) or rows (top/bottom) whose pixels are all
near-black (max channel <= 12), scanning inward. The window shot carries the
title bar (screencapture -o keeps it), so rows are scored below the first
non-uniform band only via the bottom bar; top bar is reported raw.
A frame that fills the window has left=right=0. A pure-black frame (boot)
reports bars equal to the full size; the 'lit' fraction is the control.
"""
import sys
from PIL import Image


def dark_col(px, w, h, x, y0, y1, thr):
    for y in range(y0, y1, 2):
        if max(px[x, y][:3]) > thr:
            return False
    return True


def dark_row(px, w, h, y, thr):
    for x in range(0, w, 2):
        if max(px[x, y][:3]) > thr:
            return False
    return True


def score(path, thr=12):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()
    # skip the macOS title bar: first row block that is not near-black from the top
    # is the bar itself; game content starts after ~28 pt (56 px at 2x). Score columns
    # over the middle 80% of rows so the title bar never counts.
    y0, y1 = int(h * 0.1), int(h * 0.9)
    left = 0
    while left < w and dark_col(px, w, h, left, y0, y1, thr):
        left += 1
    right = 0
    while right < w - left and dark_col(px, w, h, w - 1 - right, y0, y1, thr):
        right += 1
    bottom = 0
    while bottom < h and dark_row(px, w, h, h - 1 - bottom, thr):
        bottom += 1
    lit = sum(1 for x in range(0, w, 8) for y in range(0, h, 8) if max(px[x, y]) > thr)
    tot = len(range(0, w, 8)) * len(range(0, h, 8))
    return w, h, left, right, bottom, lit / tot


if __name__ == "__main__":
    for p in sys.argv[1:]:
        w, h, l, r, b, lit = score(p)
        print(f"{p}: {w}x{h} aspect={w / h:.3f} bar_left={l} bar_right={r} bar_bottom={b} lit={lit:.3f}")
