#!/usr/bin/env python3
"""Score the outer-terrain edge in phase-gated PPM framebuffer dumps.

Usage: g3c_edge_score.py <fbd-dir> [minimum-swap]
The edge excess is the mean terrain-pixel fraction in the left/right outer
12.5% minus the center 50%.  It is a discriminator, not a visual verdict:
the dump and nonzero whole-frame terrain fraction are required controls.
"""
import glob
import os
import re
import statistics
import sys


def load(path):
    data = open(path, "rb").read().split(b"\n", 4)
    w, h = map(int, data[2].split())
    return w, h, data[4]


def terrain_fraction(w, h, px, x0, x1):
    hits = total = 0
    for y in range(int(h * .30), int(h * .80)):
        for x in range(x0, x1):
            o = (y * w + x) * 3
            r, g, b = px[o:o + 3]
            total += 1
            if r > b + 8 or g > b + 8:
                hits += 1
    return hits / total if total else 0.0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    root = argv[1]
    minimum = int(argv[2]) if len(argv) > 2 else 0
    rows = []
    for path in sorted(glob.glob(os.path.join(root, "fb_*.ppm"))):
        match = re.search(r"fb_(\d+)_", path)
        if not match:
            continue
        n = int(match.group(1))
        if n < minimum:
            continue
        w, h, px = load(path)
        if len(px) < w * h * 3 or w < 64:
            continue
        whole = terrain_fraction(w, h, px, 0, w)
        band = max(1, w // 8)
        center = terrain_fraction(w, h, px, w // 4, (w * 3) // 4)
        left = terrain_fraction(w, h, px, 0, band)
        right = terrain_fraction(w, h, px, w - band, w)
        rows.append((n, w, whole, left, right, (left + right) / 2 - center))
    if not rows:
        print("no frames")
        return 1
    edge = [r[-1] for r in rows]
    whole = [r[2] for r in rows]
    q = lambda values, p: sorted(values)[min(len(values) - 1, int(len(values) * p))]
    widths = sorted(set(r[1] for r in rows))
    print("%s frames=%d widths=%s terrain_med=%.4f terrain_p10=%.4f edge_excess_med=%.4f edge_p90=%.4f edge_abs_p90=%.4f" % (
        os.path.basename(os.path.dirname(root.rstrip("/"))), len(rows), ",".join(map(str, widths)),
        statistics.median(whole), q(whole, .10), statistics.median(edge), q(edge, .90), q([abs(x) for x in edge], .90)))
    print("control=PASS" if statistics.median(whole) > 0 else "control=FAIL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
