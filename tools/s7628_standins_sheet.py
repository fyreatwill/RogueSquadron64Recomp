#!/usr/bin/env python3
"""s7628 G6c step 3: owner-viewable contact sheet of same-run stand-in on/off frame pairs.

Window 1 of ROGUESQ_STANDINS=frame + ROGUESQ_STANDINS_DUMP toggles stand-ins per submit call, so adjacent dumped swaps are a
same-run on/off pair a frame apart. For each arm the N pairs with the largest on-vs-off luma difference (excluding pixels that also
differ between the two OFF neighbours, i.e. camera motion) are picked; each sheet row is: ON frame | OFF frame | diff (magenta),
cropped to the bounding box of the stand-in difference (padded) and scaled up.

usage: s7628_standins_sheet.py OUT.png ARM=LOG:FBDIR [ARM=LOG:FBDIR ...] [--pairs 4] [--shimmer RATE] [--control]
Prints one line per arm: pairs considered, per chosen pair the stand-in diff px and crop box.

s7629 shimmer filter (--cluster FLOOR, default 16; 0 = off = the s7628 scorer): stand-ins are solid shapes, scene shimmer
(cliff texture aliasing at dd4) is scattered single pixels. Only diff pixels inside BLOCK x BLOCK (8x8) blocks holding >= FLOOR
set pixels survive (fpx). Calibrated s7629 on the s7628 eye-labelled arms (median clustered px/pair): L1 dd2 bunker 171,
L4 dd4 towers 1252, L1 dd4 shimmer 0, L4 dd2 none 0. A window-2 (forced-off) shimmer-cell map was tried first and REJECTED:
window 2 is ~360 frames later and its shimmer cells do not predict window 1's (L1 dd4 kept ~500 px at every rate/floor, while
the L4 towers lost half). --control paints a synthetic 24x24 block into the ON frame of every pair; PASS when each keeps
>= 288 added fpx, half the 576 painted (edge blocks and the motion mask cost up to ~1/3; s7629 min 382). Arm lines: px (raw) / fpx (clustered), med_fpx over all pairs.
"""
import re, sys, glob, os
from PIL import Image, ImageDraw, ImageChops

T = 40


CELL = 32


def load(fbdir, log, win=1):
    files = {int(re.search(r'fb_(\d+)_w', os.path.basename(p)).group(1)): p
             for p in glob.glob(os.path.join(fbdir, 'fb_*_w*.ppm')) if 'tail' not in p}
    rows = []
    for line in open(log, errors='replace'):
        m = re.search(r'\[standins-fb\] n=(\d+) win=(\d) on=(-?\d+)', line)
        if m and int(m.group(2)) == win and int(m.group(1)) in files:
            rows.append((int(m.group(1)), int(m.group(3)), files[int(m.group(1))]))
    rows.sort()
    return rows


def thresh(im):
    return im.point(lambda v: 255 if v > T else 0)


def flicker(a, b, c):
    motion = thresh(ImageChops.difference(a, c))
    d = ImageChops.subtract(thresh(ImageChops.difference(b, a)), motion)
    return ImageChops.multiply(d, thresh(ImageChops.difference(b, c)))


def pixels(im):
    return list(im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata())


BLOCK = 8


def clustered(d, floor):
    """Keep only diff pixels in BLOCK x BLOCK blocks with >= floor set pixels."""
    if floor <= 0:
        return d
    gw, gh = d.width // BLOCK, d.height // BLOCK
    g = d.crop((0, 0, gw * BLOCK, gh * BLOCK)).resize((gw, gh), Image.BOX)
    keep = g.point(lambda v: 255 if v * BLOCK * BLOCK >= floor * 255 else 0).resize((gw * BLOCK, gh * BLOCK), Image.NEAREST)
    full = Image.new('L', d.size, 0); full.paste(keep, (0, 0))
    return ImageChops.multiply(d, full)


def main():
    args = [a for a in sys.argv[1:]]
    npairs = 4
    if '--pairs' in args:
        i = args.index('--pairs'); npairs = int(args[i + 1]); del args[i:i + 2]
    floor = 16
    if '--cluster' in args:
        i = args.index('--cluster'); floor = int(args[i + 1]); del args[i:i + 2]
    control = '--control' in args
    if control:
        args.remove('--control')
    out, specs = args[0], args[1:]
    tiles = []
    for spec in specs:
        arm, rest = spec.split('=', 1)
        log, fbdir = rest.split(':', 1)
        rows = load(fbdir, log)
        cand = []; ctl = []
        for k in range(1, len(rows) - 1):
            n, on, p = rows[k]
            if on != 1 or rows[k - 1][1] != 0 or rows[k + 1][1] != 0:
                continue
            a, b, c = (Image.open(rows[j][2]).convert('L') for j in (k - 1, k, k + 1))
            if not (a.size == b.size == c.size):
                continue
            d = flicker(a, b, c)
            raw = sum(1 for v in pixels(d) if v)
            d = clustered(d, floor)
            px = sum(1 for v in pixels(d) if v)
            cand.append((px, k, d, raw))
            if control:
                x0, y0 = (37 * len(ctl)) % max(1, b.width - 40) + 8, (23 * len(ctl)) % max(1, b.height - 40) + 8
                b2 = b.copy(); v = 255 if b.getpixel((x0, y0)) < 128 else 0
                ImageDraw.Draw(b2).rectangle([x0, y0, x0 + 23, y0 + 23], fill=v)
                ctl.append(sum(1 for q in pixels(clustered(flicker(a, b2, c), floor)) if q) - px)
        cand.sort(key=lambda t: -t[0])
        med = sorted(t[0] for t in cand)[len(cand) // 2] if cand else 'na'
        print(f"arm={arm} pairs={len(cand)} cluster={floor} med_fpx={med} " +
              ' '.join(f"n{rows[k][0]}:px{raw}:fpx{px}:bbox{d.getbbox()}" for px, k, d, raw in cand[:npairs]))
        if control:
            ok = bool(ctl) and min(ctl) >= 288  # half the 576 painted px
            print(f"arm={arm} control painted={len(ctl)} min_added_fpx={min(ctl) if ctl else 'na'} {'PASS' if ok else 'FAIL'}")
        for px, k, d, raw in cand[:npairs]:
            on_im = Image.open(rows[k][2]).convert('RGB'); off_im = Image.open(rows[k - 1][2]).convert('RGB')
            # crop around the densest 32x32 cell of the stand-in diff (scattered texture shimmer would make a full-frame bbox)
            g = d.resize((max(1, d.width // 32), max(1, d.height // 32)), Image.BOX)
            gv = pixels(g); ci = max(range(len(gv)), key=lambda i: gv[i])
            cx, cy = (ci % g.width) * 32 + 16, (ci // g.width) * 32 + 16
            x0, y0 = max(0, min(on_im.width - 240, cx - 120)), max(0, min(on_im.height - 160, cy - 80))
            box = (x0, y0, min(on_im.width, x0 + 240), min(on_im.height, y0 + 160))
            mag = off_im.copy(); mag.paste((255, 0, 255), mask=d)
            crops = [im.crop(box) for im in (on_im, off_im, mag)]
            full = off_im.resize((off_im.width * 160 // off_im.height, 160)); ImageDraw.Draw(full).rectangle([v * 160 // off_im.height for v in box], outline=(255, 255, 0))
            crops.append(full)
            s = 2
            crops = [c.resize((c.width * s, c.height * s), Image.NEAREST) for c in crops[:3]] + [crops[3].resize((crops[3].width * 2, 320))]
            tiles.append((f"{arm} swap n={rows[k][0]} standin_px={raw} filtered={px} crop={box}  [label1 | label0 | diff on label0 | where]", crops))
    if not tiles:
        print('no pairs'); return 1
    W = max(sum(c.width for c in cr) + 20 for _, cr in tiles)
    H = sum(max(c.height for c in cr) + 22 for _, cr in tiles)
    sheet = Image.new('RGB', (W, H), (24, 24, 24)); dr = ImageDraw.Draw(sheet); y = 0
    for label, cr in tiles:
        dr.text((4, y + 4), label, fill=(255, 255, 255)); x = 0; y += 18
        for c in cr:
            sheet.paste(c, (x, y)); x += c.width + 10
        y += max(c.height for c in cr) + 4
    sheet.save(out)
    print(f"sheet: {out} {W}x{H} rows={len(tiles)}")


if __name__ == '__main__':
    sys.exit(main())
