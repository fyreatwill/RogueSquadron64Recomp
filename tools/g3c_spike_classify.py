#!/usr/bin/env python3
"""G3c(b): classify ROGUESQ_LOG_SPIKE [spike] lines. usage: g3c_spike_classify.py run.log
Splits flagged tris into fully-off-screen (rasteriser draws nothing) vs border-crossing
(hull of the 5 edge vertices intersects the 320x240 screen) and tabulates the pinned Y."""
import re, sys, collections
pat = re.compile(r"\[spike\] swap=(\d+) off=(\w+) op=(\w+) Y\(h,m,l\)=([-\d.]+),([-\d.]+),([-\d.]+) V=((?:\([^)]*\))+)")
off = cross = 0; pins = collections.Counter(); xs = []
for line in open(sys.argv[1], errors="replace"):
    m = pat.search(line)
    if not m: continue
    sw, yh, ym, yl = int(m[1]), float(m[4]), float(m[5]), float(m[6])
    pts = [tuple(map(float, p.split(","))) for p in re.findall(r"\(([^)]*)\)", m[7])]
    # screen intersection test on the triangle's y-span clipped to [0,240]: any edge vertex x range at visible y?
    # conservative: bbox of vertices vs screen, then check lowest on-screen vertex
    bx0 = min(p[0] for p in pts); bx1 = max(p[0] for p in pts)
    by0 = min(p[1] for p in pts); by1 = max(p[1] for p in pts)
    hit = bx1 >= 0 and bx0 <= 320 and by1 >= 0 and by0 <= 240
    if hit: cross += 1; xs.append((sw, m[3], yh, ym, yl, bx0, bx1))
    else: off += 1
    if yh == ym: pins[yh] += 1
print(f"flagged={off+cross} fully_offscreen={off} bbox_hits_screen={cross}")
print("pinned yh==ym values:", dict(pins.most_common(6)))
for r in xs[:12]: print("cross", r)
