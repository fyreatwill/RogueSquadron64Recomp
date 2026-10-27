#!/usr/bin/env python3
"""G1d: compare flat-sky 'hole' score between a 4:3 control and wide arms, flight half only, and write a top-4 sheet.
Usage: g1d_hole_count.py outdir arm=dir-of-fb_*.ppm ...   (dirs should hold only the flight-width frames)
A wide arm only shows excess holes if its late-half >0.10 fraction exceeds the control's; legit sky (climbing craft) scores high in every arm."""
import glob, os, statistics, sys
sys.path.insert(0, os.path.dirname(__file__))
src = open(os.path.join(os.path.dirname(__file__), "g3c_holes.py")).read().split("specs = sys.argv")[0]
ns = {"__file__": os.path.join(os.path.dirname(__file__), "g3c_holes.py")}; exec(src, ns)
g, score = ns["g"], ns["score"]
from PIL import Image
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for spec in sys.argv[2:]:
    arm, d = spec.split("=", 1)
    fs = sorted(glob.glob(os.path.join(d, "*.ppm"))); fs = fs[len(fs)//2:]
    sc = sorted((score(*g.load(p)[:2], g.load(p)[2]), p) for p in fs); v = [s for s, _ in sc]
    print(f"{arm}: n={len(v)} med={statistics.median(v):.3f} >0.05={sum(x>.05 for x in v)} >0.10={sum(x>.10 for x in v)}")
    ims = [Image.open(p).convert("RGB") for _, p in sc[-4:]]
    ims = [i.resize((400, int(400*i.height/i.width))) for i in ims]
    S = Image.new("RGB", (1600, max(i.height for i in ims)))
    for k, i in enumerate(ims): S.paste(i, (k*400, 0))
    S.save(os.path.join(out, f"top_{arm}.png"))
