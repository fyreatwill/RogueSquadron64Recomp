#!/usr/bin/env python3
"""G3c shake amplitude: high-frequency residual of camera yaw and camera-minus-craft heading vs a
0.25 s centred moving average (resampled to a uniform 120 Hz grid so 30 vs 60 fps arms are comparable).
Usage: g3c_hf.py LOG...   Synthetic control: g3c_hf.py --synthetic"""
import sys, math, statistics as st
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from g3c_jerk import parse

def series(rows):
    fr, prev = [], None
    for vi, t, tk, cam, pl in rows:
        if any(not math.isfinite(x) for x in cam): continue
        if prev is None or cam != prev: fr.append((t, cam, pl)); prev = cam
    return fr

def unwrap(a):
    o = [a[0]]
    for x in a[1:]:
        while x - o[-1] > math.pi: x -= 2*math.pi
        while x - o[-1] < -math.pi: x += 2*math.pi
        o.append(x)
    return o

def hf(ts, ys, turning_only=True, W=0.25, hz=120):
    # linear resample
    grid, out, j = [], [], 0
    t = ts[0]
    while t < ts[-1]:
        while ts[j+1] < t: j += 1
        f = (t-ts[j])/(ts[j+1]-ts[j]) if ts[j+1] > ts[j] else 0
        grid.append(t); out.append(ys[j]+f*(ys[j+1]-ys[j])); t += 1/hz
    n = int(W*hz/2); res = []
    for i in range(n, len(out)-n):
        sm = sum(out[i-n:i+n+1])/(2*n+1)
        rate = (out[i+n]-out[i-n])/(2*n/hz)
        if abs(rate) > 0.05: res.append(out[i]-sm)
    return len(res), (math.sqrt(sum(r*r for r in res)/len(res)) if res else float('nan'))

def run(rows, name):
    fr = series(rows)
    ts = [f[0] for f in fr]
    cam = unwrap([math.atan2(f[1][0], f[1][2]) for f in fr])
    n, a = hf(ts, cam)
    print(f"{name}: frames={len(fr)} turning-samples={n} camera-yaw HF residual rms={a*1000:.3f} mrad")

if '--synthetic' in sys.argv:
    for amp in (0, 0.02):
        rows = [(i, i/30, 0, [math.sin(0.5*i/30+(amp if i % 2 else 0)), 0, math.cos(0.5*i/30+(amp if i % 2 else 0))]+[0]*13, [0]*12) for i in range(600)]
        run(rows, f"synthetic 30fps alt-amp={amp}")
else:
    for p in sys.argv[1:]: run(parse(p), p.split('/')[-2])
