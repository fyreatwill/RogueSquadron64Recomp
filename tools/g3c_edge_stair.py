#!/usr/bin/env python3
"""Stair-step metric for the terrain/sky horizon in phase-gated PPM dumps.

Usage: g3c_edge_stair.py <fbd-dir> [min-frame] [max-frame]
Per frame: horizon y per column = first row (from 30% height down) that is not
sky (sky: b > r+15 and b >= g, or bright cloud r,g,b all > 150) for 3 rows in a
row. Only frames whose horizon is found in >=80% of columns and whose terrain
fraction below it is >40% count. stair = mean |y[x+1]-2y[x]+y[x-1]| over
columns (roughness: 0 for any straight line), jump = fraction of columns with
|dy|>=3. Control: frame count > 0 and the retail arm sets the baseline.
"""
import glob, os, re, statistics, sys


def load(path):
    d = open(path, "rb").read().split(b"\n", 4)
    w, h = map(int, d[2].split())
    return w, h, d[4]


def is_sky(r, g, b):
    return (b > r + 15 and b >= g) or (r > 150 and g > 150 and b > 150)


def horizon(w, h, px):
    ys = []
    for x in range(w):
        y0 = None
        run = 0
        for y in range(int(h * .30), int(h * .95)):
            o = (y * w + x) * 3
            if is_sky(*px[o:o + 3]):
                run = 0
            else:
                run += 1
                if run == 3:
                    y0 = y - 2
                    break
        ys.append(y0)
    return ys


def main(a):
    root = a[1]
    lo = int(a[2]) if len(a) > 2 else 0
    hi = int(a[3]) if len(a) > 3 else 10**9
    res = []
    for p in sorted(glob.glob(os.path.join(root, "fb_*_w[5-9]*.ppm")))[::4]:
        n = int(re.search(r"fb_(\d+)_", p).group(1))
        if not lo <= n <= hi:
            continue
        w, h, px = load(p)
        if len(px) < w * h * 3:
            continue
        ys = horizon(w, h, px)
        ok = [y for y in ys if y is not None]
        if len(ok) < .8 * w or statistics.median(ok) > h * .9:
            continue
        v = [y for y in ys if y is not None]
        st = statistics.mean(abs(v[i + 1] - 2 * v[i] + v[i - 1]) for i in range(1, len(v) - 1))
        jm = sum(1 for i in range(1, len(v)) if abs(v[i] - v[i - 1]) >= 3) / len(v)
        res.append((n, st, jm))
    if not res:
        print(root, "no usable frames; control=FAIL")
        return 1
    print("%s frames=%d stair_med=%.3f stair_p90=%.3f jump_med=%.3f jump_p90=%.3f control=PASS" % (
        root.split("/")[-2], len(res), statistics.median(r[1] for r in res),
        sorted(r[1] for r in res)[int(len(res) * .9)], statistics.median(r[2] for r in res),
        sorted(r[2] for r in res)[int(len(res) * .9)]))
    return 0


sys.exit(main(sys.argv))
