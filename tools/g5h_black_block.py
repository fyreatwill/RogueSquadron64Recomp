#!/usr/bin/env python3
"""s6921 G5h: find frames that are black but for one bright noisy block, the transition flash seen at t=21.9 of an AT THE MOVIES capture. Edge ring dark, inner box busy.
Prints each run of such frames: rel s, frame span, mach-second parity, box mean and spread.  g5h_black_block.py RAW [step=2]"""
import struct, os, sys
from PIL import Image, ImageStat
raw = sys.argv[1]; step = int(sys.argv[2]) if len(sys.argv) > 2 else 2
f = open(raw, 'rb'); t0, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3; n = os.path.getsize(raw) // rec
top = int(h * .09); runs = []; cur = None; dark = 0
for i in range(0, n, step):
    f.seek(i * rec); t = struct.unpack('<Q', f.read(8))[0]; g = Image.frombytes('RGB', (w, h), (f.seek(i * rec + 16), f.read(w * h * 3))[1])
    edge = (g.crop((0, top, w, top + h // 10)), g.crop((0, h - h // 12, w, h)), g.crop((0, top, w // 8, h)))
    e = max(sum(ImageStat.Stat(c).mean) / 3 for c in edge)
    hit = False
    if e < 3:
        dark += 1; s = ImageStat.Stat(g.crop((w // 8, h // 3, w - w // 8, h - h // 12)).convert('L')); hit = s.stddev[0] > 12
    if hit:
        if cur and i - cur[1] <= 4 * step: cur[1] = i
        else: cur = [i, i, (t - t0) / 24e6, (t // 24000000) & 1, round(s.mean[0], 1), round(s.stddev[0], 1)]; runs.append(cur)
print(raw, 'frames', n, 'dark-edge samples', dark, 'block runs', len(runs))
for a, b, tt, p, m, sd in runs: print(f'  t={tt:7.2f} frames {a}-{b} parity {p} box mean {m} spread {sd}')
