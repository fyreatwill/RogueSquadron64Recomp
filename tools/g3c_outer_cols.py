#!/usr/bin/env python3
"""G3c(a): outer-15% vs centre-70% column horizon jump score + contact sheet.
Usage: g3c_outer_cols.py <outdir> arm=lo-hi:fbd-dir ..."""
import glob, os, re, statistics, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import g3c_horizon_score as g

def tops(w, h, px, bins=128):
    y0, y1 = int(h*.15), int(h*.85); out = []
    for b in range(bins):
        x = min(w-1, int((b+.5)*w/bins)); top = None; run = 0
        for y in range(y0, y1):
            o = (y*w+x)*3; r, gg, bl = px[o:o+3]
            if r > bl+8 or gg > bl+8:
                run += 1
                if run == 3: top = y-2; break
            else: run = 0
        out.append(top)
    return out

def jf(t, h, lo, hi):
    p = [(a, b) for a, b in zip(t[lo:hi], t[lo+1:hi+1]) if a is not None and b is not None]
    return (sum(1 for a, b in p if abs(a-b) > .015*h)/len(p) if p else None, len(p))

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for spec in sys.argv[2:]:
    arm, rest = spec.split("=", 1); rng, d = rest.split(":", 1); lo, hi = map(int, rng.split("-"))
    fs = []
    for p in sorted(glob.glob(os.path.join(d, "fb_*.ppm"))):
        n = int(re.search(r"fb_(\d+)_", p).group(1))
        if lo <= n <= hi: fs.append(p)
    L, C, R, ctrl = [], [], [], 0
    for p in fs:
        w, h, px = g.load(p)
        if len(px) < w*h*3 or w < 64: continue
        t = tops(w, h, px)
        if any(v is not None for v in t): ctrl += 1
        for lst, (a, b) in ((L, (0, 19)), (C, (19, 109)), (R, (109, 127))):
            v, n = jf(t, h, a, b)
            if v is not None: lst.append(v)
    m = lambda l: round(statistics.median(l), 3) if l else None
    print(f"{arm}: frames={len(fs)} ctrl={ctrl} jumpL={m(L)} jumpC={m(C)} jumpR={m(R)}")
    for i, k in enumerate(fs[::max(1, len(fs)//3)][:3]):
        w, h, px = g.load(k)
        Image.frombytes("RGB", (w, h), px[:w*h*3]).save(f"{out}/{arm}_{i}.png")
