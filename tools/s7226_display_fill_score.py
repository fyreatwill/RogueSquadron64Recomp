#!/usr/bin/env python3
"""s7226: does a FULLSCREEN game fill the display it opened on? Scores `screencapture -D n` shots of one display
(DIR/shot_ARM_T.png) against the boot log's game aspect (DIR/log_ARM.txt "[g1d] ... FB_WIDTH=N": FB_WIDTH/448).
Per shot: lit bbox (rows/cols with >2% pixels above luma 24, at 1/4 scale, 2-px edge trim) as fractions of the display,
lit pixel aspect. FILL = bbox >=0.97 both axes; BARS = short in one axis and lit aspect within 3% of the game aspect.
Positive control per arm: first FILL/BARS shot with 20% black pasted at both sides must read x0>=0.19, x1<=0.81.
usage: s7226_display_fill_score.py DIR ARM [ARM ...]"""
import sys, re, glob
from PIL import Image
d = sys.argv[1]
def bbox(a):
    s = a.resize((max(1, a.size[0] // 4), max(1, a.size[1] // 4)), Image.BOX)
    s = s.crop((2, 2, s.size[0] - 2, s.size[1] - 2)); W, H = s.size; p = s.load()
    rows = [y for y in range(H) if sum(p[x, y] > 24 for x in range(W)) > 0.02 * W]
    cols = [x for x in range(W) if sum(p[x, y] > 24 for y in range(H)) > 0.02 * H]
    return (cols[0] / W, rows[0] / H, (cols[-1] + 1) / W, (rows[-1] + 1) / H) if rows and cols else None
for arm in sys.argv[2:]:
    log = open(f'{d}/log_{arm}.txt', errors='replace').read()
    fb = re.findall(r'FB_WIDTH=(\d+)', log); fbw = int(fb[-1]) if fb else 640; ga = fbw / 448 if fbw > 640 else 4 / 3
    tally = {}; ctl = None
    shots = sorted(glob.glob(f'{d}/shot_{arm}_*.png'), key=lambda q: int(re.search(r'_(\d+)\.png$', q)[1]))
    print(f'== {arm}: FB_WIDTH {fbw} (game aspect {ga:.4f}), {len(shots)} shots')
    for q in shots:
        a = Image.open(q).convert('L'); b = bbox(a); t = re.search(r'_(\d+)\.png$', q)[1]
        if not b: tally['dark'] = tally.get('dark', 0) + 1; continue
        la = (b[2] - b[0]) * a.size[0] / ((b[3] - b[1]) * a.size[1]); da = a.size[0] / a.size[1]
        full = b[2] - b[0] > 0.97 and b[3] - b[1] > 0.97
        v = ('FILL' if abs(da / ga - 1) <= 0.03 else 'STRETCH') if full else ('BARS' if abs(la / ga - 1) < 0.03 else '?')
        tally[v] = tally.get(v, 0) + 1
        print(f'  t={t:>3} disp {a.size[0]}x{a.size[1]} ({da:.3f}) bbox ({b[0]:.3f},{b[1]:.3f},{b[2]:.3f},{b[3]:.3f}) lit {la:.3f} -> {v}')
        if ctl is None and v in ('FILL', 'BARS'): ctl = a
    print('  SUMMARY', tally)
    if ctl:
        c = ctl.copy(); w = c.size[0]; c.paste(0, (0, 0, w // 5, c.size[1])); c.paste(0, (w - w // 5, 0, w, c.size[1])); b = bbox(c)
        print('  CONTROL side-black bbox', tuple(round(x, 3) for x in b) if b else None, '->', 'PASS' if b and b[0] >= 0.19 and b[2] <= 0.81 else 'FAIL')
