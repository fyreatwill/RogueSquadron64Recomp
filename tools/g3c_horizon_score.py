#!/usr/bin/env python3
"""Horizon-profile scorer for G3c(a): jagged far-terrain edge.

Usage: g3c_horizon_score.py <fbd-dir> [min-frame] [stride]
Per frame, per column: topmost row (y in 15%..85%) starting a 3-pixel terrain run
(terrain = r>b+8 or g>b+8, same rule as g3c_edge_score.py). Metrics, normalised to
frame size so 512- and 1024-wide dumps compare:
  jump  = fraction of adjacent column pairs (columns binned to 1/128 width) whose
          topmost row differs by > 1.5% of height  (stair-step / blocky edge)
  hole  = fraction of sky-coloured pixels below the topmost terrain row, in the
          band between horizon and 85% height (missing cells)
Control: terrain_cols (columns with any terrain) must be > 0 on every frame.
"""
import glob, os, re, statistics, sys


def load(path):
    d = open(path, "rb").read().split(b"\n", 4)
    w, h = map(int, d[2].split())
    return w, h, d[4]


def score(w, h, px):
    y0, y1 = int(h * .15), int(h * .85)
    bins = 128
    tops = []
    holes = tot = 0
    for b in range(bins):
        x = min(w - 1, int((b + .5) * w / bins))
        top = None
        run = 0
        for y in range(y0, y1):
            o = (y * w + x) * 3
            r, g, bl = px[o:o + 3]
            if r > bl + 8 or g > bl + 8:
                run += 1
                if run == 3 and top is None:
                    top = y - 2
                    break
            else:
                run = 0
        tops.append(top)
        if top is not None:
            for y in range(top, y1):
                o = (y * w + x) * 3
                r, g, bl = px[o:o + 3]
                tot += 1
                if not (r > bl + 8 or g > bl + 8) and bl > r + 8 and bl > g + 8:
                    holes += 1
    pairs = [(a, b) for a, b in zip(tops, tops[1:]) if a is not None and b is not None]
    jumps = sum(1 for a, b in pairs if abs(a - b) > .015 * h)
    return (jumps / len(pairs) if pairs else 0.0, holes / tot if tot else 0.0,
            sum(1 for t in tops if t is not None))


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    root = argv[1]
    mn = int(argv[2]) if len(argv) > 2 else 0
    stride = int(argv[3]) if len(argv) > 3 else 1
    rows = []
    files = sorted(glob.glob(os.path.join(root, "fb_*.ppm")))[::stride]
    for p in files:
        m = re.search(r"fb_(\d+)_", p)
        if not m or int(m.group(1)) < mn:
            continue
        w, h, px = load(p)
        if len(px) < w * h * 3 or w < 64:
            continue
        j, ho, c = score(w, h, px)
        if c:
            rows.append((j, ho, c))
    if not rows:
        print("no frames / control FAIL"); return 1
    q = lambda v, p: sorted(v)[min(len(v) - 1, int(len(v) * p))]
    J = [r[0] for r in rows]; H = [r[1] for r in rows]
    print("%s n=%d jump_med=%.3f jump_p90=%.3f hole_med=%.4f hole_p90=%.4f cols_med=%d" % (
        os.path.basename(os.path.dirname(root.rstrip("/"))), len(rows),
        statistics.median(J), q(J, .9), statistics.median(H), q(H, .9), statistics.median(r[2] for r in rows)))
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
