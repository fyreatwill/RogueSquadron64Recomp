#!/usr/bin/env python3
"""G3c(a): flat sky-colour area in the LOWER half of the frame (holes through terrain show as flat sky blue).
Score per frame = fraction of lower-half pixels within 6/255 of the sky-hole colour, where the hole colour is the
sky colour sampled from frame row 0.78*h in the retail-independent way: most frequent blue-dominant colour in the lower half
(0 if no blue colour covers >0.2% of the lower half). Only frames with >50% non-black pixels are scored.
Usage: g3c_holes.py arm=lo-hi:fbd-dir ...  (first arm also gets a synthetic positive control)"""
import collections, glob, os, re, statistics, sys
sys.path.insert(0, os.path.dirname(__file__))
import g3c_horizon_score as g

def score(w, h, px):
    cnt = collections.Counter()
    for y in range(h//2, h, 2):
        for x in range(0, w, 2):
            o = (y*w+x)*3; cnt[(px[o]>>2, px[o+1]>>2, px[o+2]>>2)] += 1
    tot = sum(cnt.values()); best = None
    for (r, gg, b), c in cnt.most_common(8):
        if b > r+8 and b > 40: best = (r, gg, b); break
    if not best: return 0.0
    return sum(c for (r, gg, b), c in cnt.items() if abs(r-best[0]) <= 2 and abs(gg-best[1]) <= 2 and abs(b-best[2]) <= 2) / tot

def frames(spec):
    arm, rest = spec.split("=", 1); rng, d = rest.split(":", 1); lo, hi = map(int, rng.split("-"))
    return arm, [p for p in sorted(glob.glob(os.path.join(d, "fb_*.ppm")))
                 if lo <= int(re.search(r"fb_(\d+)_", p).group(1)) <= hi]

def good(w, h, px): return len(px) >= w*h*3 and w >= 64 and sum(1 for i in range(0, w*h*3, 97) if px[i] > 20) > .5*(w*h*3/97)

specs = sys.argv[1:]
for sp in specs:
    arm, fs = frames(sp); v = []
    for p in fs:
        w, h, px = g.load(p)
        if good(w, h, px): v.append(score(w, h, px))
    q = sorted(v)
    print(f"{arm}: n={len(v)} med={statistics.median(v):.4f} p90={q[int(.9*(len(q)-1))]:.4f} max={q[-1]:.4f} frames>0.03={sum(1 for x in v if x>.03)}")
arm, fs = frames(specs[0])
for p in fs:
    w, h, px = g.load(p)
    if good(w, h, px) and score(w, h, px) < 1e-3: break
b = bytearray(px[:w*h*3]); base = score(w, h, b)
for cx, cy in ((.25, .8), (.5, .85), (.75, .8)):
    for y in range(int(cy*h)-30, int(cy*h)+30):
        for x in range(int(cx*w)-50, int(cx*w)+50): b[(y*w+x)*3:(y*w+x)*3+3] = bytes((135, 195, 230))
print("positive control", os.path.basename(p), "base", round(base, 4), "injected 3 flat-sky patches", round(score(w, h, b), 4))
