#!/usr/bin/env python3
"""Camera-independent rendering metric for a capture burst.

Session 18's lesson: this scene animates and every run is an independent
play-through, so comparing frame n of run A with frame n of run B compares two
different camera positions, and dominant-colour summaries hide the difference
entirely. Aggregating pixel CLASSES over every frame of a run does not care
where the camera was.

Run the game with ROGUESQ_FORCE_FILL=FF00FF so the background fill is a colour
that appears nowhere in the art. Then:

  magenta%  - background fill
  black%    - geometry that rendered black (the session 18 bug)
  other%    - geometry that rendered with actual content  <-- the number to move
  distinct  - distinct colours among "other" pixels

A fix for "textured geometry renders black" shows up as other% rising from
~zero, whatever the camera was doing.

Usage: pixel_stats.py <dir>...
"""
import glob
import os
import sys

from PIL import Image


def is_magenta(p):
    return p[0] > 120 and p[2] > 120 and p[1] < p[0] - 50 and p[1] < p[2] - 50


def stats(d):
    tot = mag = blk = 0
    others = set()
    other = 0
    for f in sorted(glob.glob(os.path.join(d, "*.png"))):
        # Crop the window chrome; the title bar is not the game.
        im = Image.open(f).convert("RGB").crop((8, 30, 632, 506))
        for p in im.getdata():
            tot += 1
            if is_magenta(p):
                mag += 1
            elif max(p) < 24:
                blk += 1
            else:
                other += 1
                others.add((p[0] >> 3, p[1] >> 3, p[2] >> 3))
    if tot == 0:
        return None
    return (100.0 * mag / tot, 100.0 * blk / tot, 100.0 * other / tot, len(others), tot)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    print(f"{'run':<34} {'magenta%':>9} {'black%':>8} {'other%':>8} {'distinct':>9}")
    for d in argv[1:]:
        s = stats(d)
        if s is None:
            print(f"{os.path.basename(d):<34}  (no frames)")
            continue
        mag, blk, other, distinct, _ = s
        print(f"{os.path.basename(d):<34} {mag:9.1f} {blk:8.1f} {other:8.2f} {distinct:9d}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
