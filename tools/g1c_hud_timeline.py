#!/usr/bin/env python3
"""s6409 G1c ph2: per-frame HUD radar-ring presence timeline over a fixed-dd fb dump dir; reports HUD-absent runs
(frame index, run length) so absences can be tested for clustering/periodicity. Usage: g1c_hud_timeline.py <fbd_dir> [min_n]"""
import sys, os, glob, re
d = sys.argv[1]; minn = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
def load(p):
    b = open(p, "rb").read(); h = b.split(b"\n", 4); w, hh = map(int, h[2].split()); return w, hh, h[4]
rows = []
for p in sorted(glob.glob(os.path.join(d, "fb_*_w512.ppm"))):
    n = int(re.search(r"fb_(\d+)_", p).group(1))
    if n < minn: continue
    w, h, px = load(p); c = 0
    for y in range(20, 150):
        for x in range(380, 490):
            o = (y*w+x)*3
            if px[o] > 150 and px[o+1] < 60 and px[o+2] < 60: c += 1
    rows.append((n, c))
ab = [n for n, c in rows if c == 0]
print(f"frames={len(rows)} hud_absent={len(ab)}")
runs = []; 
for n in ab:
    if runs and n - runs[-1][1] <= 3: runs[-1][1] = n; runs[-1][2] += 1
    else: runs.append([n, n, 1])
print("runs(start,end,count):", [tuple(r) for r in runs][:60])
print("n of absent:", ab[:80])
