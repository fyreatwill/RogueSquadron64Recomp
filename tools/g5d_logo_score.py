#!/usr/bin/env python3
"""s6903 G5d: Factor 5 logo completeness in a g5b_capture .raw. Per frame, share of bright (max channel > 110) pixels in the central picture band, peak of a 1 s median over t0..t1, split left/right of the picture centre.
A full FACTOR + bolt scores both halves; the cut logo loses the left half. usage: g5d_logo_score.py x.raw [t0=38] [t1=44]"""
import struct, sys, statistics
from PIL import Image
raw = sys.argv[1]; t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 38; t1 = float(sys.argv[3]) if len(sys.argv) > 3 else 44
f = open(raw, 'rb'); b, w, h = struct.unpack('<QII', f.read(16)); f.seek(0); fs = w*h*3; S = []
while True:
    hd = f.read(16); d = f.read(fs)
    if len(d) < fs: break
    t = (struct.unpack('<Q', hd[:8])[0]-b)/24e6
    if t < t0 or t > t1: continue
    m = Image.frombytes('RGB', (w, h), d).split(); mx = Image.merge('RGB', m).convert('L').point(lambda v: 255 if v > 110 else 0)
    y0, y1 = int(h*.2), int(h*.8); L = mx.crop((0, y0, w//2, y1)).histogram()[255]; R = mx.crop((w//2, y0, w, y1)).histogram()[255]
    S.append((t, L/(w//2*(y1-y0)), R/(w//2*(y1-y0))))
best = (0, 0, 0)
for t, _, _ in S[::10]:
    wnd = [s for s in S if t <= s[0] < t+1]
    if len(wnd) > 3:
        l = statistics.median(s[1] for s in wnd); r = statistics.median(s[2] for s in wnd)
        # settled logo: least-changing window, keeps explosion out by taking the frame group with the highest left share below title onset
        if l+r > best[1]+best[2] and l+r < .35: best = (t, l, r)
print(f'{raw.split("/")[-1]}: best 1 s window at {best[0]:.1f} s left {best[1]:.4f} right {best[2]:.4f}')
