#!/usr/bin/env python3
"""Tile a capture burst into one labelled contact sheet.

Judging a run means seeing how the scene evolves, and opening frames one at a
time is both slow and easy to mislead yourself with — a single frame cannot
tell a static screen from a moving camera. This lays a burst out as a grid with
each cell labelled by its filename, so one image answers "what happened during
this capture".

Usage: contact_sheet.py <out.png> <frame.png...> [--cols N] [--cell W]
       contact_sheet.py <out.png> <dir> [--every N]
"""
import sys
import os
import glob

from PIL import Image, ImageDraw

CELL = 300
COLS = 4


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    out = argv[1]
    rest = argv[2:]
    cols, cell, every = COLS, CELL, 1
    files = []
    i = 0
    while i < len(rest):
        a = rest[i]
        if a == "--cols":
            cols = int(rest[i + 1]); i += 2
        elif a == "--cell":
            cell = int(rest[i + 1]); i += 2
        elif a == "--every":
            every = int(rest[i + 1]); i += 2
        else:
            if os.path.isdir(a):
                files.extend(sorted(glob.glob(os.path.join(a, "*.png"))))
            else:
                files.append(a)
            i += 1
    files = files[::every]
    if not files:
        print("no frames")
        return 1

    rows = (len(files) + cols - 1) // cols
    label_h = 14
    sheet = Image.new("RGB", (cols * cell, rows * (cell + label_h)), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    for n, f in enumerate(files):
        im = Image.open(f).convert("RGB")
        im.thumbnail((cell, cell))
        x = (n % cols) * cell
        y = (n // cols) * (cell + label_h)
        sheet.paste(im, (x, y + label_h))
        draw.text((x + 2, y + 2), os.path.basename(f)[:40], fill=(200, 200, 200))
    sheet.save(out)
    print(f"{out}  {len(files)} frames  {sheet.size[0]}x{sheet.size[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
