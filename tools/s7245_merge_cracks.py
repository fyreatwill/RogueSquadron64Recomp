#!/usr/bin/env python3
# s7245 WIDEWIN merge image judgement. Input: a g5b_capture raw (16-byte <QII mach,w,h header + w*h RGB per frame) from a
# same-run =tog arm (rs64_tog_odd: s = mach/24e6, phase = (s ^ s>>3) & 1, xor8 default). Per frame (in flight, middle of its
# second so the tog phase has reached the screen) it counts CRACK pixels: a pixel that differs from BOTH neighbours 2 px away
# (horizontally or vertically) by > T while those two neighbours agree within T/2 -- a 1-2 px seam through otherwise
# continuous ground, the signature of a T-junction gap at a merged-cell border. Counted in the terrain band (rows below the
# brightest-sky rows: lower 3/4 of the frame, HUD-free middle columns) and split into thirds by column (L/C/R side edges).
# POSITIVE CONTROL (same run): every off frame gets 2 synthetic 1-px seams (+80 per channel) (one horizontal 120 px in the left third,
# one vertical 0.2h in the right third) drawn into a copy; the detector must count >= 100 more seam px on >= 90% of copies.
# Output: per-phase mean crack px per frame (+ per third), Welch-ish split by 8 s block (A/A: off frames in even vs odd
# blocks) and an owner sheet of off|on pairs with 2x crack close-ups.
# usage: s7245_merge_cracks.py raw out.png [label_off] [label_on] [rows=4]
import sys, struct, statistics as st
from PIL import Image, ImageDraw, ImageChops as IC
raw, out = sys.argv[1], sys.argv[2]
lo = sys.argv[3] if len(sys.argv) > 3 else 'off'; lh = sys.argv[4] if len(sys.argv) > 4 else 'on'
ROWS = int(sys.argv[5]) if len(sys.argv) > 5 else 4
T = 40
f = open(raw, 'rb'); _, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3; n = f.seek(0, 2) // rec
def hdr(i): f.seek(i * rec); return struct.unpack('<QII', f.read(16))[0]
def img(i): f.seek(i * rec + 16); return Image.frombytes('RGB', (w, h), f.read(w * h * 3))
def inflight(im): return sum(im.getpixel((x, 200))[0] for x in (5, 10, 15)) >= 30
def content_w():   # the captured window can be narrower than the capture: black columns at the right
    f.seek(n // 2 * rec + 16); im = Image.frombytes('RGB', (w, h), f.read(w * h * 3)).convert('L'); x = w - 1
    while x > w // 2 and max(im.getpixel((x, y)) for y in range(h // 4, h, h // 16)) < 8: x -= 1
    return x + 1
CWD = content_w()
Y0, Y1 = h * 35 // 100, h * 75 // 100; X0, X1 = CWD // 16, CWD - CWD // 16; W3 = (X1 - X0) // 3
def gt(im, t): return im.point(lambda v: 255 if v > t else 0)
def lt(im, t): return im.point(lambda v: 255 if v < t else 0)
def mask(g, dx, dy):
    a = IC.offset(g, dx, dy); b = IC.offset(g, -dx, -dy)
    return IC.multiply(IC.multiply(gt(IC.subtract(g, a), T), gt(IC.subtract(g, b), T)), lt(IC.difference(a, b), T // 2))
def cracks(im):
    g = im.crop((X0, Y0, X1, Y1)).convert('L')
    m = IC.lighter(mask(g, 2, 0), mask(g, 0, 2)); m = m.crop((2, 2, m.width - 2, m.height - 2))
    th = [m.crop((k * W3, 0, min((k + 1) * W3, m.width), m.height)).histogram()[255] for k in range(3)]
    return th[0] + th[2], th, m   # side thirds only: the centre holds the craft/reticle, WW cells live at the sides
def seam(im):   # +80 per channel along two 1-px lines: a seam just above the detector contrast (T=40 L), in the band
    a = im.copy(); px = a.load(); yL = h * 55 // 100; xR = X1 - W3 // 2
    for x in range(X0 + W3 // 2 - 60, X0 + W3 // 2 + 60): px[x, yL] = tuple(min(255, v + 80) for v in px[x, yL])
    for y in range(h * 45 // 100, h * 65 // 100): px[xR, y] = tuple(min(255, v + 80) for v in px[xR, y])
    return a
sel = {}
for i in range(n):
    t = hdr(i); s = int(t // 24000000); ph = abs((t / 24e6) % 1 - 0.5)
    if ph < 0.3 and (s not in sel or ph < sel[s][0]): sel[s] = (ph, i)
secs = sorted(sel)[2:-2]
res = {0: [], 1: []}; ctl = []; blk = {0: [], 1: []}; keep = {}
for s in secs:
    a = img(sel[s][1])
    if not inflight(a): continue
    p = (s ^ (s >> 3)) & 1; c, th, _ = cracks(a); res[p].append((c, th)); keep[s] = p
    if p == 0:
        ctl.append(cracks(seam(a))[0] - c); blk[(s >> 3) & 1].append(c)
def mean(v): return st.mean(v) if v else float('nan')
print('frames', n, 'w', w, 'h', h, 'content_w', CWD, 'flight secs off', len(res[0]), 'on', len(res[1]))
cp = sum(1 for d in ctl if d >= 100)
print('CONTROL %s (synthetic seams +%.0f crack px median, %d/%d frames >= 100)' % ('PASS' if ctl and cp >= 0.9 * len(ctl) else 'FAIL', st.median(ctl) if ctl else 0, cp, len(ctl)))
for p, lab in ((0, lo), (1, lh)):
    v = res[p]; print('%-8s crack px/frame %.1f  thirds L/C/R %s' % (lab, mean([x[0] for x in v]), ' '.join('%.1f' % mean([x[1][k] for x in v]) for k in range(3))))
d = mean([x[0] for x in res[1]]) - mean([x[0] for x in res[0]]); aa = mean(blk[1]) - mean(blk[0])
print('on-off %+.1f crack px/frame; A/A (off frames, odd-even 8 s blocks) %+.1f' % (d, aa))
# sheet: ROWS adjacent off/on pairs spread over flight, each with a 2x close-up of the left third far band
pairs = [(s, s + 1) for s in sorted(keep) if s + 1 in keep and keep[s] != keep[s + 1]]
pick = [pairs[int(k * (len(pairs) - 1) / max(ROWS - 1, 1))] for k in range(ROWS)] if len(pairs) >= ROWS else pairs
W2, H2 = w // 2, h // 2; CW, CH = w // 3, h // 4
sheet = Image.new('RGB', (2 * (W2 + CW) + 18, len(pick) * (max(H2, CH * 2) + 18) + 4), (20, 20, 20)); dr = ImageDraw.Draw(sheet)
for r, pr in enumerate(pick):
    pr = sorted(pr, key=lambda s: keep[s]); y = r * (max(H2, CH * 2) + 18) + 18
    for c, s in enumerate(pr):
        im = img(sel[s][1]); a = im; x = c * (W2 + CW + 12)
        sheet.paste(im.resize((W2, H2)), (x, y))
        crop = im.crop((X0, h * 2 // 5, X0 + CW // 2, h * 2 // 5 + CH // 2)).resize((CW, CH), Image.NEAREST); sheet.paste(crop, (x + W2 + 4, y))
        dr.text((x + 4, y - 15), '%s  second %d  cracks %d' % ((lo, lh)[keep[s]], s - secs[0], cracks(a)[0]), fill=(255, 255, 255))
sheet.save(out); print('sheet', out, len(pick), 'pairs')
# seam highlight sheet: the 3 off and 3 on flight frames with the most side-third seam px, band crop, seam px in red, full width
allf = sorted(((c[0], s) for s in keep for c in [cracks(img(sel[s][1]))]), reverse=True)
top = [s for _, s in allf if keep[s] == 0][:3] + [s for _, s in allf if keep[s] == 1][:3]
BH = Y1 - Y0; hs = Image.new('RGB', (X1 - X0, len(top) * (BH + 16)), (20, 20, 20)); dh = ImageDraw.Draw(hs)
for r, s in enumerate(top):
    im = img(sel[s][1]); c, th, m = cracks(im); band = im.crop((X0, Y0, X1, Y1)); bp = band.load(); mp = m.load()
    for y in range(m.height):
        for x in range(m.width):
            if mp[x, y] and not (W3 <= x + 2 < 2 * W3): bp[x + 2, y + 2] = (0, 255, 255)
    hs.paste(band, (0, r * (BH + 16) + 16)); dh.text((4, r * (BH + 16) + 2), '%s second %d side seam px %d (L %d R %d)' % ((lo, lh)[keep[s]], s - secs[0], c, th[0], th[2]), fill=(255, 255, 255))
o2 = out.rsplit('.', 1)[0] + '_seams.png'; hs.save(o2); print('seams', o2)
per = {p: sorted(c for c, s in allf if keep[s] == p) for p in (0, 1)}
print('side seam px quartiles off %s on %s' % ([per[0][len(per[0]) * k // 4] for k in (1, 2, 3)], [per[1][len(per[1]) * k // 4] for k in (1, 2, 3)]))
