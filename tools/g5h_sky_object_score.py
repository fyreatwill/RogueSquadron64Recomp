#!/usr/bin/env python3
"""s6917 G5h: how much object lives in the sky, per toggle second, from a g5b_capture raw of a =tog run (odd mach second = lever on).
Score per frame: share of pixels above the sea edge that are not sky. Sky is R < G < B with B bright; a beam (R ~ G) or a dark ship is not.
The sea edge is found per column pair as the first row, from the top, that reads as sea (dark blue), so terrain and sea never count.
Frames within --skip s after a toggle edge are dropped: they carry the old state. Control: each second is compared with its two neighbours, so a slow change of the scene cannot read as a step.

  g5h_sky_object_score.py RAW --t0 13 --t1 22 [--top 22] [--skip 0.25]
"""
import argparse, os, struct, statistics as st
from PIL import Image

def score(im, top):
    w, h = im.size; p = im.load(); obj = sky = 0
    for x in range(0, w, 4):
        for y in range(top, h, 2):
            r, g, b = p[x, y]
            if b < 110 and r < 70 and g < 95 and b > r + 25 and y > h * .25: break  # sea
            if r < g - 4 and g < b - 4 and b > 150: sky += 1
            else: obj += 1
    return obj / max(1, obj + sky)

a = argparse.ArgumentParser(); a.add_argument('raw'); a.add_argument('--t0', type=float, default=0); a.add_argument('--t1', type=float, default=1e9)
a.add_argument('--top', type=int, default=22); a.add_argument('--skip', type=float, default=.25); a = a.parse_args()
f = open(a.raw, 'rb'); t0, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3; n = os.path.getsize(a.raw) // rec
S = {}
for i in range(0, n, 6):
    f.seek(i * rec); t = struct.unpack('<Q', f.read(8))[0]; f.seek(i * rec + 16); rel = (t - t0) / 24e6
    if not a.t0 <= rel < a.t1 or (t / 24e6) % 1 < a.skip: continue
    S.setdefault(t // 24000000, []).append(score(Image.frombytes('RGB', (w, h), f.read(w * h * 3)), a.top))
ks = sorted(S); M = {k: st.median(S[k]) for k in ks}
for k in ks: print(f't={(k * 24000000 - t0) / 24e6:6.1f} {"on " if k & 1 else "off"} {M[k]:.4f} n={len(S[k])}')
on = [M[k] / max(1e-6, st.mean([M[j] for j in (k - 1, k + 1) if j in M])) for k in ks[1:-1] if k & 1]
off = [M[k] / max(1e-6, st.mean([M[j] for j in (k - 1, k + 1) if j in M])) for k in ks[1:-1] if not k & 1]
print('median ratio to neighbour seconds: on', round(st.median(on), 2) if on else None, 'off', round(st.median(off), 2) if off else None)
