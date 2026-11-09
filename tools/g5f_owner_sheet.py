#!/usr/bin/env python3
"""G5f owner sheet: clamp-off long lines beside clamp-on neighbours, same run.

usage: g5f_owner_sheet.py <capture.raw> <lines.txt> <out.png> <max_frame> [n=6] [minlen=100]

lines.txt is scratch/s6906/g5f_lines output: frame tick x0 y0 x1 y1 len fill r g b clamp inj.
Rows: for up to n clamp-off (clamp=0) lines >= minlen px (not injected, VI phase 0.2-0.9, frame < max_frame),
left = f-1/f/f+1 crops around the line, right = the same crop in the nearest clamp-on frame
(+-90 frames) and its neighbours. Below: per-bucket line counts off / on over frames < max_frame.
"""
import sys, struct
from PIL import Image, ImageDraw

raw, lines, out, maxf = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
N = int(sys.argv[5]) if len(sys.argv) > 5 else 6
MINL = int(sys.argv[6]) if len(sys.argv) > 6 else 100
f = open(raw, 'rb'); t, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3
f.seek(0, 2); nfr = f.tell() // rec

def frame(i):
    f.seek(i * rec + 16); return Image.frombytes('RGB', (w, h), f.read(w * h * 3))

R = [l.split() for l in open(lines)]
R = [r for r in R if len(r) >= 13 and r[-1] == '0' and int(r[0]) < maxf]
clampof = {}  # frame -> clamp state (from any line in that frame)
for r in R: clampof[int(r[0])] = int(r[-2])
ph = lambda r: (int(r[1]) / 24e6) % 1
off = [r for r in R if r[-2] == '0' and int(r[6]) >= MINL and 0.2 <= ph(r) <= 0.9]
# one per event: skip lines within 3 frames of a picked one
pick = []
for r in sorted(off, key=lambda r: -int(r[6])):
    fi = int(r[0])
    if all(abs(fi - int(p[0])) > 30 for p in pick): pick.append(r)
    if len(pick) >= N: break
pick.sort(key=lambda r: int(r[0]))

# clamp state from each frame's own capture tick: W_CLAMP=tog is on in odd 24 MHz seconds.
# Frames at phase < 0.05 or > 0.95 can be rendered in the neighbouring second (s7005: 4 "on" knife lines at
# phase 0.003 were off-second renders), so on-crops require all three frames at phase 0.2-0.9.
def tick(i):
    f.seek(i * rec); return struct.unpack('<Q', f.read(8))[0]
def state(i):
    q = tick(i) / 24e6; p = q % 1
    return int(q) % 2 if 0.2 <= p <= 0.9 else -1
CW, CH, Z = 240, 150, 2
def crop(i, x0, y0, x1, y1):
    cx = min(max((x0 + x1) // 2 - CW // 2, 0), w - CW); cy = min(max((y0 + y1) // 2 - CH // 2, 0), h - CH)
    return frame(i).crop((cx, cy, cx + CW, cy + CH)).resize((CW * Z, CH * Z), Image.NEAREST)

tw, th = CW * Z, CH * Z; gap = 6; lab = 18
sheet = Image.new('RGB', (6 * tw + 5 * gap + 40, len(pick) * (th + lab + gap) + 260), (30, 30, 30))
d = ImageDraw.Draw(sheet)
d.text((10, 2), f"G5f: LEFT clamp OFF (f-1, f, f+1) | RIGHT clamp ON (nearest frame triple mid-second, same crop). {raw.split('/')[-1]}", fill=(255, 255, 0))
y = 20
for r in pick:
    fi = int(r[0]); x0, y0, x1, y1 = map(int, r[2:6])
    on = next((fi + dlt * s for dlt in range(1, 91) for s in (1, -1)
               if 1 <= fi + dlt * s < min(maxf, nfr) - 1 and all(state(fi + dlt * s + k) == 1 for k in (-1, 0, 1))), None)
    d.text((10, y), f"off f{fi} len {r[6]} px ({x0},{y0})-({x1},{y1})   on f{on}", fill=(255, 255, 255))
    for k, i in enumerate([fi - 1, fi, fi + 1]):
        sheet.paste(crop(i, x0, y0, x1, y1), (10 + k * (tw + gap), y + lab))
    if on is not None:
        for k, i in enumerate([on - 1, on, on + 1]):
            sheet.paste(crop(i, x0, y0, x1, y1), (40 + (3 + k) * (tw + gap), y + lab))
    y += th + lab + gap
B = [(20, 40), (40, 60), (60, 100), (100, 99999)]
cnt = {(b, c): 0 for b in B for c in (0, 1)}
for r in R:
    if not 0.05 <= ph(r) <= 0.95: continue  # toggle-edge frames may belong to the other arm
    L = int(r[6])
    for b in B:
        if b[0] <= L < b[1]: cnt[(b, int(r[-2]))] += 1
d.text((10, y + 10), f"lines per length bucket, frames < {maxf}, VI phase 0.05-0.95, off / on:", fill=(255, 255, 0))
for k, b in enumerate(B):
    d.text((10, y + 30 + 18 * k), f"{b[0]}-{b[1] - 1 if b[1] < 99999 else ''} px: {cnt[(b, 0)]} / {cnt[(b, 1)]}", fill=(255, 255, 255))
sheet.save(out)
for r in pick: print('pick', ' '.join(r[:7]))
for b in B: print('bucket', b, cnt[(b, 0)], cnt[(b, 1)])
