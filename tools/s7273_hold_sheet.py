#!/usr/bin/env python3
"""s7273 G5c: contact sheet of every image hold >= min_ms in a tools/g5b_capture .raw, so each hold can be classified as
load-side (scene transition / black / wipe) or in-flight. Per hold, one row: frame 1 s before, the held image, the first
image after the hold, frame 1 s after. Row label: capture time, hold ms, tog3 phase, and whether it overlaps a control
window. Also prints a per-hold mean-luma / changed-pixel line (black/fade frames read as luma < 20).
usage: s7273_hold_sheet.py RAW OUT.jpg [min_ms=250] [ctl_file|-] [scale=0.5]"""
import struct, sys, hashlib
from PIL import Image, ImageDraw
raw, out = sys.argv[1], sys.argv[2]
mn = float(sys.argv[3]) if len(sys.argv) > 3 else 250
ctl = []
if len(sys.argv) > 4 and sys.argv[4] != '-':
    ctl = [tuple(map(int, l.split()[:2])) for l in open(sys.argv[4]) if len(l.split()) >= 2]
sc = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
f = open(raw, 'rb'); t0, w, h = struct.unpack('<QII', f.read(16)); fs = w * h * 3; rec = 16 + fs
# pass 1: timestamps + change points (record index of each change)
ts = []; chg = []; prev = None; i = 0; f.seek(0)
while True:
    hd = f.read(16); b = f.read(fs)
    if len(hd) < 16 or len(b) < fs: break
    t = struct.unpack('<Q', hd[:8])[0]; ts.append(t)
    d = hashlib.blake2b(b, digest_size=16).digest()
    if d != prev: chg.append(i); prev = d
    i += 1
def img(k):
    k = max(0, min(len(ts) - 1, k)); f.seek(k * rec + 16)
    return Image.frombytes('RGB', (w, h), f.read(fs))
def at(t):  # record index nearest capture tick t
    import bisect
    return max(0, min(len(ts) - 1, bisect.bisect_left(ts, t)))
def luma(im):
    g = im.convert('L').resize((64, 32)); px = list(g.getdata()); return sum(px) / len(px)
rows = []
for a, b in zip(chg, chg[1:]):
    ms = (ts[b] - ts[a]) / 24e3
    if ms < mn: continue
    c = any(ts[a] <= ce + 24000000 and ts[b] >= cs for cs, ce in ctl)
    rows.append((a, b, ms, (ts[a] // 24000000) % 3, (ts[a] - t0) / 24e6, c))
tw, th = int(w * sc), int(h * sc); lab = 18
S = Image.new('RGB', (tw * 4, max(1, len(rows)) * (th + lab)), (40, 40, 40)); D = ImageDraw.Draw(S)
for r, (a, b, ms, ph, t, c) in enumerate(rows):
    fr = [img(at(ts[a] - 24000000)), img(a), img(b), img(at(ts[b] + 24000000))]
    y = r * (th + lab)
    D.text((4, y + 2), f"+{t:.2f}s hold {ms:.0f} ms ph{ph}{' CONTROL' if c else ''} | -1s | held | next | +1s", fill=(255, 255, 0))
    for j, im in enumerate(fr): S.paste(im.resize((tw, th)), (j * tw, y + lab))
    print(f"+{t:.2f}s {ms:.0f}ms ph{ph} ctl={int(c)} luma pre/held/next/post {' '.join(f'{luma(x):.0f}' for x in fr)}")
S.save(out, quality=85); print(f"rows {len(rows)} -> {out}")
