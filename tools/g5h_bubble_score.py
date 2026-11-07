#!/usr/bin/env python3
"""s6923 G5h: score and sheet a capture (g5b_capture raw) for the lava-shot shield bubble.
  g5h_bubble_score.py RAW OUT.png [T0 T1 [STEP]]
Per frame: fraction of pixels (below the title bar) with min(r,g,b) > 35, the bright pale or blue shield against the dark lava scene.
Prints p50, p90 and max over T0..T1 s of the capture and writes a sheet of frames every STEP s."""
import struct, os, sys, bisect
from PIL import Image, ImageChops, ImageStat, ImageDraw
p, out = sys.argv[1], sys.argv[2]
T0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0; T1 = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9; ST = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
f = open(p, 'rb'); t0, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3; n = os.path.getsize(p) // rec
ts = []
for i in range(n): f.seek(i * rec); ts.append((struct.unpack('<Q', f.read(8))[0] - t0) / 24e6)
v = []
def frame(i): f.seek(i * rec + 16); return Image.frombytes('RGB', (w, h), f.read(w * h * 3))
for i in range(0, n, 3):
    if not T0 <= ts[i] <= T1: continue
    r, g, b = frame(i).crop((0, 20, w, h)).split()
    v.append(ImageStat.Stat(ImageChops.darker(ImageChops.darker(r, g), b).point(lambda x: 255 if x > 35 else 0)).mean[0] / 255)
v.sort(); print(p, 'frames', n, 'dur %.1f' % ts[-1], 'scored', len(v), 'p50 %.3f p90 %.3f max %.3f' % (v[len(v) // 2], v[int(len(v) * .9)], v[-1]) if v else '')
want = []; t = max(T0, 0)
while t <= min(T1, ts[-1]) and len(want) < 36: want.append(t); t += ST
W, H = 192, 108; sh = Image.new('RGB', (W * 6, (H + 12) * ((len(want) + 5) // 6)), (20, 20, 20)); d = ImageDraw.Draw(sh)
for j, t in enumerate(want):
    i = min(bisect.bisect(ts, t), n - 1); x = (j % 6) * W; y = (j // 6) * (H + 12)
    sh.paste(frame(i).resize((W, H)), (x, y + 12)); d.text((x + 2, y), '%.2f' % ts[i], fill=(255, 255, 0))
sh.save(out)
