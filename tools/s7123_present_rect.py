#!/usr/bin/env python3
"""s7123: presented picture rectangle in WINDOW coordinates from a g5b_capture raw, padding-aware.

ScreenCaptureKit scales the window into the W x H capture preserving its aspect and pads the rest with black, anchored
top-left (measured s7123: a 640x512 pt window into 320x240 fills x 0..299, x 300..319 is padding). Reading the picture
rect against the full capture width therefore makes a centred picture look off-centre (s7122 reported 21/66 px margins;
the truth is 43/45). This tool finds the window extent from the title bar (rows that are non-black edge to edge) and the
picture extent (non-black columns/rows below the title bar), and reports the picture in window points.

Control (built in): the title bar must span a contiguous column range that starts at x 0; if it does not, the window
extent cannot be trusted and the tool exits 2. Expected picture boxes printed for comparison:
  fb box   : VI fbSize (cols x rows, square pixels) fitted to the client area (RT64 default, VI_SHAPE off)
  vi shape : cols*1024/xScale x lines (ROGUESQ_VI_SHAPE=1, the retail TV shape, s6928)

usage: s7123_present_rect.py <raw> <win_w_pt> <win_h_pt> [--frames a,b,c] [--fb 512x448] [--xscale 0x333] [--title 32]
exit 0 = picture centred within 2 window pt, 1 = off-centre, 2 = control failed
"""
import os, struct, sys


def frame(path, i):
    f = open(path, 'rb'); _, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3
    n = os.path.getsize(path) // rec
    i = min(i, n - 1); f.seek(i * rec + 16)
    return w, h, n, f.read(w * h * 3)


def main(a):
    if len(a) < 3: print(__doc__); return 2
    raw, ww, wh = a[0], float(a[1]), float(a[2]); opts = dict(zip(a[3::2], a[4::2]))
    fbw, fbh = map(int, opts.get('--fb', '512x448').split('x')); xs = int(opts.get('--xscale', '0x333'), 16)
    title = float(opts.get('--title', '32'))
    w, h, n, _ = frame(raw, 0)
    frames = [int(x) for x in opts['--frames'].split(',')] if '--frames' in opts else [n // 4, n // 2, 3 * n // 4]
    s = min(w / ww, h / wh)  # SCK fit scale, capture px per window pt
    print('capture %dx%d, %d frames, fit scale %.4f px/pt -> window occupies %.1f x %.1f px' % (w, h, n, s, ww * s, wh * s))
    worst = 0.0; ok = True
    for fi in frames:
        _, _, _, px = frame(raw, fi)
        lum = lambda x, y: sum(px[(y * w + x) * 3:(y * w + x) * 3 + 3])
        trows = int(title * s) - 1
        tb = [x for x in range(w) if any(lum(x, y) > 30 for y in range(0, max(1, trows)))]
        if not tb or tb[0] > 1 or (tb[-1] - tb[0] + 1) < 0.9 * ww * s:
            print('frame %d CONTROL FAIL: title bar cols %s' % (fi, (tb[0], tb[-1]) if tb else None)); ok = False; continue
        winx1 = tb[-1] + 1  # first padding column
        y0 = trows + 2
        cols = [x for x in range(winx1) if any(lum(x, y) > 30 for y in range(y0, h, 3))]
        rows = [y for y in range(y0, h) if any(lum(x, y) > 30 for x in range(0, winx1, 2))]
        if not cols or not rows: print('frame %d: no picture' % fi); continue
        L = cols[0] / s; R = (winx1 - cols[-1] - 1) / s
        print('frame %d: window cols 0..%d (pad %d..%d) | picture x %.1f..%.1f pt (%.1f wide), y %.1f..%.1f (%.1f tall) | margins L %.1f R %.1f'
              % (fi, winx1 - 1, winx1, w - 1, cols[0] / s, (cols[-1] + 1) / s, (cols[-1] + 1 - cols[0]) / s,
                 rows[0] / s - title, (rows[-1] + 1) / s - title, (rows[-1] + 1 - rows[0]) / s, L, R))
        worst = max(worst, abs(L - R))
    cw, ch = ww, wh - title
    for name, bw, bh in (('fb box', fbw, fbh), ('vi shape', fbw * 1024.0 / xs, fbh)):
        k = min(cw / bw, ch / bh); print('expected %-8s %.1f x %.1f pt, margins %.1f each side' % (name, bw * k, bh * k, (cw - bw * k) / 2))
    if not ok: return 2
    print('verdict: %s (worst |L-R| %.1f pt; capture resolution %.1f pt)' % ('CENTRED' if worst <= 2.5 else 'OFF-CENTRE', worst, 1 / s))
    return 0 if worst <= 2.5 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
