#!/usr/bin/env python3
"""s7098 G5b: near-wall flicker rate, normalised by wall-hug time, from one g5b_capture raw + its g5b_drops csv.
wall-hug frame: >= WALL share of sampled pixels in the 3D area (title bar and the HUD top band skipped) are dark (luma < 70).
event: a transient (g5b_drops) with T >= 0.12, t >= 5 s, whose preceding frame is wall-hug. The s7098 a6 replay showed every such
event is the near canyon wall missing from the RDP stream itself (angrylion paints the same hole).
usage: s7098_wall_flicker.py raw drops.csv [WALL=0.85]"""
import sys, struct, os
raw, dcsv = sys.argv[1], sys.argv[2]; WALL = float(sys.argv[3]) if len(sys.argv) > 3 else 0.85
f = open(raw, 'rb'); t0, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3; n = os.path.getsize(raw) // rec
hug = bytearray(n); T = [0] * n
ys = range(40, h, 6); xs = range(0, 370, 6)
for i in range(n):
    f.seek(i * rec); T[i] = struct.unpack('<Q', f.read(8))[0]; f.seek(i * rec + 16); px = f.read(w * h * 3)
    d = c = 0
    for y in ys:
        r = y * w * 3
        for x in xs:
            j = r + 3 * x; c += 1
            if px[j] * 3 + px[j + 1] * 6 + px[j + 2] < 700: d += 1
    hug[i] = d >= WALL * c
ev = 0; evs = []
for k, line in enumerate(open(dcsv)):
    if k == 0: continue
    p = line.split(','); x, ts, Tt = int(p[0]), float(p[1]), float(p[4])
    if Tt >= 0.12 and ts >= 5 and x > 0 and hug[x - 1]: ev += 1; evs.append(round(ts, 1))
hs = sum((T[i + 1] - T[i]) / 24e6 for i in range(n - 1) if hug[i] and T[i + 1] - T[i] < 2.4e6)
span = (T[-1] - T[0]) / 24e6
ep = sum(1 for i, t in enumerate(evs) if i == 0 or t - evs[i - 1] > 1.0)  # episodes: events more than 1 s apart
print('frames %d span %.1fs wall-hug %.1fs (%.0f%%) events %d episodes %d rate %.3f ep/hug-min  times %s' % (n, span, hs, 100 * hs / span, ev, ep, 60 * ep / hs if hs else 0, evs[:40]))
