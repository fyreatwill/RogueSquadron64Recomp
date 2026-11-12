#!/usr/bin/env python3
"""s7225: does the picture follow a LIVE window resize (ASPECT=auto vs fixed)? Full-desktop screencapture -x shots of a
windowed RETINA=0 run on the 2x built-in (pixels = 2 x points). The window origin is the boot log's
"[g1f] window WxH fullscreen=0 at X,Y" row (SDL keeps the top-left on SDL_SetWindowSize). The CURRENT window width is
read from the shot itself: the title-bar band 14 pt above the content top is one uniform colour exactly as wide as the
window; the height is the known size for that width (boot size or a ROGUESQ_WIN_TEST_RESIZE_S entry). Per shot:
  lit bbox inside the content crop (rows/cols with >2% pixels above luma 24) as fractions, and the lit picture's pixel
  aspect, against the window aspect and the boot game aspect (FB_WIDTH/448 -> RT64 output aspect).
  verdict: FILL (bbox ~full both axes), BARS (lit aspect ~ game aspect, short in one axis), STRETCH (fills a window whose
  aspect differs from the game aspect by >3%), ? otherwise.
Positive control per arm: the first FILL/BARS crop with 20% black pasted at left and right must report bbox x0>=0.19,
x1<=0.81 and lit aspect reduced by ~0.6x.
usage: s7225_resize_aspect_score.py DIR ARM [ARM ...]  (DIR/shot_ARM_T.png, DIR/log_ARM.txt)"""
import sys, re, glob
from PIL import Image
d = sys.argv[1]
def bbox(a):
    # cols from the bottom 80% only, rows from the left 60% only: a macOS notification banner can sit over the top-right
    s = a.resize((max(1, a.size[0] // 4), max(1, a.size[1] // 4)), Image.BOX)
    s = s.crop((2, 2, s.size[0] - 2, s.size[1] - 2))  # the window's 1-pt grey border reads as lit
    W, H = s.size; p = s.load()
    rows = [y for y in range(H) if sum(p[x, y] > 24 for x in range(int(0.6 * W))) > 0.02 * 0.6 * W]
    cols = [x for x in range(W) if sum(p[x, y] > 24 for y in range(int(0.2 * H), H)) > 0.02 * 0.8 * H]
    return (cols[0] / W, rows[0] / H, (cols[-1] + 1) / W, (rows[-1] + 1) / H) if rows and cols else None
def edge_ok(img, X, Y, ww):
    # title-bar colour (sampled right of the traffic lights) just inside the candidate right edge, not just outside it
    p = img.load(); y = 2 * (Y - 14); c = p[2 * (X + 80), y][:3]
    same = lambda q: max(abs(a - b) for a, b in zip(p[q, y][:3], c)) <= 6
    xi, xo = 2 * (X + ww) - 12, 2 * (X + ww) + 12
    return xo < img.size[0] and same(xi) and not same(xo)
for arm in sys.argv[2:]:
    log = open(f'{d}/log_{arm}.txt', errors='replace').read()
    w = re.findall(r'\[g1f\] window (\d+)x(\d+) fullscreen=0 at (-?\d+),(-?\d+)', log)
    fb = re.findall(r'FB_WIDTH=(\d+)', log); rz = re.findall(r'test resize t=([\d.]+) (\d+)x(\d+)', log)
    if not w: print(f'== {arm}: no window row'); continue
    W0, H0, X, Y = (int(v) for v in w[0]); fbw = int(fb[-1]) if fb else 640; ga = fbw / 448 if fbw > 640 else 4 / 3
    sizes = {W0: H0}; sizes.update({int(a): int(b) for _, a, b in rz})
    print(f'== {arm}: boot window {W0}x{H0} at {X},{Y}  FB_WIDTH {fbw} (game aspect {ga:.3f})  resizes {rz}')
    ctl = None; tally = {}; seen = False
    for t in sorted(int(re.search(r'_(\d+)\.png', q)[1]) for q in glob.glob(f'{d}/shot_{arm}_*.png')):
        img = Image.open(f'{d}/shot_{arm}_{t}.png').convert('RGB')
        hit = [k for k in sizes if edge_ok(img, X, Y, k)]
        if len(hit) == 1: ww = hit[0]; seen = True; how = 'edge'
        else:  # edge hidden (banner) or ambiguous: boot size before the first edge-identified resize, else the last resize
            ww = W0 if not seen else int(rz[-1][1]); how = 'time'
        wh = sizes[ww]
        a = img.convert('L').crop((2 * X, 2 * Y, 2 * (X + ww), 2 * (Y + wh))); b = bbox(a)
        if not b: print(f'  t={t:3d} win {ww}x{wh} dark'); continue
        la = (b[2] - b[0]) * ww / ((b[3] - b[1]) * wh); wa = ww / wh
        full = b[2] - b[0] > 0.97 and b[3] - b[1] > 0.97
        v = ('STRETCH' if abs(wa / ga - 1) > 0.03 else 'FILL') if full else ('BARS' if abs(la / ga - 1) < 0.03 else '?')
        tally.setdefault((ww, wh, v), []).append(t)
        print(f'  t={t:3d} [{how}] win {ww}x{wh} (aspect {wa:.3f}) bbox ({b[0]:.3f},{b[1]:.3f},{b[2]:.3f},{b[3]:.3f}) lit aspect {la:.3f} -> {v}')
        if ctl is None and v in ('FILL', 'BARS'): ctl = (a, la, ww, wh)
    for k, ts in tally.items(): print(f'  SUMMARY win {k[0]}x{k[1]}: {k[2]} x{len(ts)}')
    if ctl:
        a, la, ww, wh = ctl; c = a.copy(); cw = a.size[0]; c.paste(0, (0, 0, cw // 5, a.size[1])); c.paste(0, (cw - cw // 5, 0, cw, a.size[1]))
        b = bbox(c); l2 = (b[2] - b[0]) * ww / ((b[3] - b[1]) * wh) if b else 0
        ok = b and b[0] >= 0.19 and b[2] <= 0.81 and l2 < 0.7 * la
        print(f'  CONTROL side-black bbox {tuple(round(x, 3) for x in b) if b else None} lit aspect {l2:.3f} (was {la:.3f}) ->', 'PASS' if ok else 'FAIL')
