#!/usr/bin/env python3
"""s6840 G3: score window captures for the s6602-class "high-roughness band" (stale/garbage colour noise block).

Pure PIL (no numpy on this host). Per capture: crop the letterbox (luma > --black), resample the content to the
game framebuffer width (--fbw, height proportional), threshold the max-channel colour step at 1-2 px in x/y > --grad, average it
over --tile x --tile FB-px tiles, and flag tiles whose rough fraction > --frac. A band = the largest 4-connected set
of flagged tiles; a capture is BANDED when that set has >= --min-tiles tiles (default 30: natural content tops at 23 tiles (title logo), the s6602 real noise crop scores 49, an injected s6602-width band 119-527).

Positive controls (run them in the same invocation; a null is worthless without them):
  --inject x0,x1   also score a copy of every capture with random RGB noise pasted over FB columns x0..x1
                   (full content height) -- must come back BANDED.
  a real artifact crop (e.g. the s6602 RDRAM-dump noise strip) passed as an ordinary file must come back BANDED.

usage: g3_band_scan.py --fbw 796 [--inject 269,334] [--json out.json] FILES...
"""
import argparse, json, random, sys
from PIL import Image, ImageChops


def content(im, black, chrome):
    im = im.crop((0, chrome, im.width, im.height))  # window title bar (screencapture -l keeps it)
    g = im.convert('L')
    bb = g.point(lambda v: 255 if v > black else 0).getbbox()
    return im.crop(bb) if bb else im


def score(im, a):
    W = a.fbw
    H = max(a.tile, round(W * im.height / im.width))
    g = im.convert('RGB').resize((W, H), Image.BOX)
    # max-channel |d| at offsets 1 and 2 in x and y: chroma noise survives, 2-px grain is not hidden inside a block
    r = None
    for ox, oy in ((1, 0), (2, 0), (0, 1), (0, 2)):
        d = ImageChops.difference(g, ImageChops.offset(g, ox, oy)).split()
        d = ImageChops.lighter(ImageChops.lighter(d[0], d[1]), d[2])
        r = d if r is None else ImageChops.lighter(r, d)
    r = r.point(lambda v: 255 if v > a.grad else 0)
    # offset() wraps: blank the wrapped first column/row so frame edges never read as rough
    r.paste(0, (0, 0, 2, H)); r.paste(0, (0, 0, W, 2))
    tw, th = W // a.tile, H // a.tile
    t = r.crop((0, 0, tw * a.tile, th * a.tile)).resize((tw, th), Image.BOX)
    px = t.load()
    flag = {(x, y) for y in range(th) for x in range(tw) if px[x, y] / 255.0 > a.frac}
    best, seen = [], set()
    for s in flag:
        if s in seen:
            continue
        comp, st = [], [s]; seen.add(s)
        while st:
            x, y = st.pop(); comp.append((x, y))
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if n in flag and n not in seen:
                    seen.add(n); st.append(n)
        if len(comp) > len(best):
            best = comp
    bbox = None
    if best:
        xs = [c[0] for c in best]; ys = [c[1] for c in best]
        bbox = [min(xs) * a.tile, min(ys) * a.tile, (max(xs) + 1) * a.tile - 1, (max(ys) + 1) * a.tile - 1]
    return {'fb': [W, H], 'flagged': len(flag), 'tiles': tw * th, 'band_tiles': len(best), 'band_bbox_fb': bbox,
            'banded': len(best) >= a.min_tiles}


def inject(im, a, x0, x1):
    im = im.convert('RGB').copy()
    sx = im.width / a.fbw
    X0, X1 = int(x0 * sx), int((x1 + 1) * sx)
    rnd = random.Random(6840)
    # 2x2-FB-px noise blocks, the grain of the s6602 strip
    bs = max(1, int(2 * sx))
    for y in range(0, im.height, bs):
        for x in range(X0, X1, bs):
            im.paste((rnd.randrange(256), rnd.randrange(256), rnd.randrange(256)), (x, y, min(x + bs, X1), y + bs))
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--fbw', type=int, required=True)
    ap.add_argument('--black', type=int, default=8)
    ap.add_argument('--chrome', type=int, default=64, help='title-bar rows to drop (64 = retina window cap; 0 for fb crops)')
    ap.add_argument('--grad', type=int, default=48)
    ap.add_argument('--tile', type=int, default=16)
    ap.add_argument('--frac', type=float, default=0.55)
    ap.add_argument('--min-tiles', type=int, default=30)
    ap.add_argument('--inject')
    ap.add_argument('--json')
    a = ap.parse_args()
    rows = []
    for f in a.files:
        im = content(Image.open(f).convert('RGB'), a.black, a.chrome)
        row = {'file': f, **score(im, a)}
        if a.inject:
            x0, x1 = map(int, a.inject.split(','))
            c = score(inject(im, a, x0, x1), a)
            row['inject'] = {'banded': c['banded'], 'band_tiles': c['band_tiles'], 'band_bbox_fb': c['band_bbox_fb']}
        rows.append(row)
        print(f"{f} band_tiles={row['band_tiles']} banded={int(row['banded'])} bbox={row['band_bbox_fb']} "
              f"flagged={row['flagged']}/{row['tiles']}"
              + (f" | inject banded={int(row['inject']['banded'])} tiles={row['inject']['band_tiles']}"
                 f" bbox={row['inject']['band_bbox_fb']}" if a.inject else ''))
    n = len(rows); b = sum(r['banded'] for r in rows)
    summ = {'n': n, 'banded': b, 'max_band_tiles': max(r['band_tiles'] for r in rows)}
    if a.inject:
        summ['inject_banded'] = sum(r['inject']['banded'] for r in rows)
    print('SUMMARY', json.dumps(summ))
    if a.json:
        json.dump({'args': vars(a), 'summary': summ, 'rows': rows}, open(a.json, 'w'), indent=1)


if __name__ == '__main__':
    sys.exit(main())
