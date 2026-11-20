#!/usr/bin/env python3
"""s7698: do the POOLMIN toggle flips change the picture? For consecutive intro fb dumps (same phase as s7698_kept_split.py), mean
abs luminance diff per band (sky 0-25%, horizon 25-55%, ground 55-100%) for pairs that straddle a mach-second flip vs pairs within
one arm. Camera motion is in both groups; a visible cap effect adds to the straddling group only. Usage: <run dir> <level>"""
import sys, os, re, ctypes, time, statistics as st
from PIL import Image, ImageChops, ImageStat
D, LV = sys.argv[1], int(sys.argv[2]); lib = ctypes.CDLL(None); lib.mach_absolute_time.restype = ctypes.c_uint64
OFF = time.time() - lib.mach_absolute_time() / 24e6
L = open(D + "/run.log", errors="replace").read().splitlines()
cine = next(i for i, l in enumerate(L) if (("[poolx] cap" in l and "-> 4096" in l) if LV < 0 else ("[cineBody] call#" in l and re.search(r"a0=0x0*%X " % LV, l))))   # s7700: LV<0 = AT THE MOVIES, range from the first cutscene-pool cap
mis = len(L) if LV < 0 else next((i for i, l in enumerate(L) if i > cine and "[poolx] cap 2048" in l), len(L))   # s7699: no flight line = intro ran to the kill (L5)
fs = []
for i, l in enumerate(L[cine:mis]):
    m = re.match(r"\[fbdump\] n=(\d+) .*stride=(\d+)", l)
    if m:
        p = "%s/fb/fb_%07d_w%s.ppm" % (D, int(m[1]), m[2])
        if os.path.exists(p): fs.append((p, os.stat(p).st_mtime - OFF))
B = ((0, .25), (.25, .55), (.55, 1.0)); g = {True: [[], [], []], False: [[], [], []]}
for (a, ta), (b, tb) in zip(fs, fs[1:]):
    A, Bm = Image.open(a).convert("L"), Image.open(b).convert("L")
    if A.size != Bm.size or tb - ta > 0.5: continue
    flip = int(ta) != int(tb); w, h = A.size
    for k, (y0, y1) in enumerate(B):
        box = (0, int(h * y0), w, int(h * y1)); g[flip][k].append(ImageStat.Stat(ImageChops.difference(A.crop(box), Bm.crop(box))).mean[0])
for f in (True, False):
    print("%-9s n=%d  " % ("straddle" if f else "within", len(g[f][0])) + "  ".join("%s p50=%.2f mean=%.2f" % (nm, st.median(v), st.mean(v)) for nm, v in zip(("sky", "horizon", "ground"), g[f]) if v))
