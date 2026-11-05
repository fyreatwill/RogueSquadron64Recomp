#!/usr/bin/env python3
"""s6903 G5d: distinct-image rate per second of a g5b_capture .raw between t0 and t1 (s from first frame). A frame counts as new if its mean abs difference to the previous kept frame exceeds thr (default 0 = any byte).
usage: g5d_distinct.py x.raw t0 t1 [thr=0]"""
import struct, sys
from PIL import Image, ImageChops, ImageStat
import statistics
raw = sys.argv[1]; t0, t1 = float(sys.argv[2]), float(sys.argv[3]); thr = float(sys.argv[4]) if len(sys.argv) > 4 else 0
f = open(raw, 'rb'); b, w, h = struct.unpack('<QII', f.read(16)); f.seek(0); fs = w*h*3; prev = None; per = {}; T = []; 
while True:
    hd = f.read(16); d = f.read(fs)
    if len(d) < fs: break
    t = (struct.unpack('<Q', hd[:8])[0]-b)/24e6
    if t < t0 or t > t1: continue
    a = Image.frombytes('RGB', (w, h), d)
    new = prev is None or (d != pb if thr == 0 else sum(ImageStat.Stat(ImageChops.difference(a, prev)).mean)/3 > thr)
    if new: prev = a; pb = d; per[int(t)] = per.get(int(t), 0)+1; T.append(t)
g = sorted((y-x)*1e3 for x, y in zip(T, T[1:])) or [0]
print(f'{raw.split("/")[-1]} t {t0}-{t1}: distinct {len(T)} ({len(T)/(t1-t0):.1f}/s) gap p50 {g[len(g)//2]:.0f} p90 {g[len(g)*9//10]:.0f} max {g[-1]:.0f} ms; per s', [per.get(s, 0) for s in range(int(t0), int(t1))])
