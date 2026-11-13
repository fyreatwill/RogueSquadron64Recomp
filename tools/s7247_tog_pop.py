#!/usr/bin/env python3
# s7247 tog HOLE scorer for same-run =tog captures (g5b_capture raw: 16-byte <QII mach,w,h + w*h RGB per frame).
# Question: does a far-terrain lever (WIDEWIN_R cell skip, MERGE) remove VISIBLE terrain? Terrain is grainy at 1 px; haze, sky,
# clouds and a hole filled by haze are smooth. Per frame: TEX = fraction of pixels in the HUD-free side thirds (rows 18-88%)
# whose local gradient |dL/dx|+|dL/dy| > G. Removing visible far cells lowers TEX in the lever's ON phase.
# Phase p(s) = (s ^ s>>3) & 1, s = floor(mach/24e6) (rs64_tog_odd); lever on in phase 1.
# (1) FLIP test: per boundary s|s+1, d = median TEX over [s+1.4, s+1.9) - median over [s+0.5, s+0.95) (both windows inside one
#     phase after the ~0.3 s latency); D = -d for off->on flips, +d for on->off flips (D > 0 = lever removes texture).
#     Same-phase boundaries give the motion floor of d (sd). Effect = mean D(switch) with its sem, vs the same-phase sd.
# (2) PHASE MEANS: mean TEX over mid-second frames by phase (as s7245), A/A = off frames split by 8 s block parity.
# POSITIVE CONTROL (same run, both tests): copies of the after-window frames of every same-phase boundary, and of every off
# mid-second frame, get their most textured 200x40 side window replaced by its own mean (terrain turned to haze): the
# detector must see a TEX drop of >= 25% of the patch area on >= 90% of copies (G=3: about 30% of band px are textured).
# usage: s7247_tog_pop.py raw [G=12]
import sys, struct, bisect, statistics as st
from PIL import Image, ImageChops as IC, ImageFilter
raw = sys.argv[1]; G = int(sys.argv[2]) if len(sys.argv) > 2 else 3
f = open(raw, 'rb'); _, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3; n = f.seek(0, 2) // rec
ts = []
for i in range(n):
    f.seek(i * rec); ts.append(struct.unpack('<QII', f.read(16))[0] / 24e6)
def img(i): f.seek(i * rec + 16); return Image.frombytes('RGB', (w, h), f.read(w * h * 3))
def inflight(im): return sum(im.getpixel((x, 200))[0] for x in (5, 10, 15)) >= 30
def content_w():
    im = img(n // 2).convert('L'); x = w - 1
    while x > w // 2 and max(im.getpixel((x, y)) for y in range(h // 4, h, h // 16)) < 8: x -= 1
    return x + 1
CWD = content_w()
X0, X1 = CWD // 16, CWD - CWD // 16; W3 = (X1 - X0) // 3; YA, YB = h * 18 // 100, h * 88 // 100
PAREA = 200 * 40
BAND = 2 * W3 * (YB - YA)
def texmask(g):
    dx = IC.difference(g, IC.offset(g, 1, 0)); dy = IC.difference(g, IC.offset(g, 0, 1))
    return IC.add(dx, dy).point(lambda v: 255 if v > G else 0)
CAND = [(x, y) for x0 in (X0, X1 - W3) for x in range(x0, x0 + W3 - 200, 100) for y in range(YA, YB - 40, 40)]
def tex(im, patch=False):
    g = im.convert('L'); m = texmask(g)
    if patch:   # control: the most textured 200x40 window (terrain) is replaced by its mean (turned to haze)
        x, y = max(CAND, key=lambda c: m.crop((c[0], c[1], c[0] + 200, c[1] + 40)).histogram()[255]); box = (x, y, x + 200, y + 40)
        g.paste(g.crop(box).resize((1, 1), Image.BOX).getpixel((0, 0)), box); m = texmask(g)
    return sum(m.crop((x0, YA, x0 + W3, YB)).histogram()[255] for x0 in (X0, X1 - W3)) / BAND
def phase(s): return (s ^ (s >> 3)) & 1
def win(a, b, patch=False):
    i0, i1 = bisect.bisect_left(ts, a), bisect.bisect_left(ts, b); idx = list(range(i0, i1, 3))
    return st.median(tex(img(i), patch) for i in idx) if len(idx) >= 3 else None
s0, s1 = int(ts[0]) + 3, int(ts[-1]) - 3
flip = []; same = []; ctl1 = []
for s in range(s0, s1):
    ia = bisect.bisect_left(ts, s + 0.5); ib = bisect.bisect_left(ts, s + 1.9) - 1
    if ib <= ia or not (inflight(img(ia)) and inflight(img(ib))): continue
    b = win(s + 0.5, s + 0.95); a = win(s + 1.4, s + 1.9)
    if a is None or b is None: continue
    d = a - b
    if phase(s) != phase(s + 1): flip.append(-d if phase(s) == 0 else d)
    else:
        same.append(d); ctl1.append(a - win(s + 1.4, s + 1.9, True))
# phase means (mid-second frame, as s7245)
sel = {}
for i in range(n):
    s = int(ts[i]); ph = abs(ts[i] % 1 - 0.5)
    if ph < 0.3 and (s not in sel or ph < sel[s][0]): sel[s] = (ph, i)
pm = {0: [], 1: []}; blk = {0: [], 1: []}; ctl2 = []
for s in sorted(sel)[2:-2]:
    im = img(sel[s][1])
    if not inflight(im): continue
    t = tex(im); p = phase(s); pm[p].append(t)
    if p == 0: blk[(s >> 3) & 1].append(t); ctl2.append(t - tex(im, True))
def mean(v): return st.mean(v) if v else float('nan')
def sem(v): return (st.stdev(v) / len(v) ** 0.5) if len(v) > 1 else float('nan')
need = 0.25 * PAREA / BAND; c = ctl1 + ctl2; cp = sum(1 for x in c if x >= need)
print('frames', n, 'w', w, 'h', h, 'content_w', CWD, 'G', G, 'flips', len(flip), 'same', len(same), 'phase frames off', len(pm[0]), 'on', len(pm[1]))
print('CONTROL %s (200x40 patch -> its mean: TEX drop median %.4f, need %.4f; %d/%d pass)' % (
    'PASS' if c and cp >= 0.9 * len(c) else 'FAIL', st.median(c) if c else 0, need, cp, len(c)))
sd = st.stdev(same) if len(same) > 1 else float('nan')
print('FLIP  D mean %+.4f +- %.4f (sem, n=%d); same-phase d mean %+.4f sd %.4f (n=%d)' % (mean(flip), sem(flip), len(flip), mean(same), sd, len(same)))
dpm = mean(pm[1]) - mean(pm[0]); aa = mean(blk[1]) - mean(blk[0])
print('PHASE TEX off %.4f on %.4f  on-off %+.4f  (A/A off by 8 s block %+.4f)' % (mean(pm[0]), mean(pm[1]), dpm, aa))
vis = mean(flip) > 2 * sem(flip) and mean(flip) > need / 2
print('VERDICT', 'LEVER REMOVES VISIBLE TEXTURE' if vis else 'no texture removed above the floor',
      '(flip effect %.2f%% of band = %.0f px; control patch = %.0f px)' % (100 * mean(flip), mean(flip) * BAND, PAREA))
