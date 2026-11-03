#!/usr/bin/env python3
"""s6856 owner sheet: 21:9 in-flight frames with the radar-region shift defaults (ZGATE+CFLIP, TEXRECT=0).

One row per level: N full flight frames (fb_<VI>_w1024.ppm at or after --from-vi) plus a 2x crop of the
radar box (x 760..1024, y 0..160 of the 1024-wide image) from the first of them.
Usage: owner_sheet_s6856.py <out.png> <label>=<fbd_dir>:<from_vi | =vi | vi,vi,...> [...] [--n 3] [--w 1024] [--cx 760]
--w picks the frame width glob (796 for 16:9), --cx the left edge of the radar crop (s6858: 500 at 796).
"""
import glob, os, re, sys
from PIL import Image, ImageDraw


def load(p):
    return Image.open(p).convert('RGB')


def main(argv):
    opt = {'--n': 3, '--w': 1024, '--cx': 760}
    for k in opt:
        if k in argv:
            i = argv.index(k); opt[k] = int(argv[i + 1]); del argv[i:i + 2]
    n, w, cx = opt['--n'], opt['--w'], opt['--cx']
    out, specs = argv[1], argv[2:]
    rows = []
    for s in specs:
        label, rest = s.split('=', 1)
        d, vi0 = rest.rsplit(':', 1)
        want = None
        if ',' in vi0 or vi0.startswith('='):
            want = {int(v) for v in vi0.lstrip('=').split(',')}
        fr = []
        for p in glob.glob(os.path.join(d, f'fb_*_w{w}.ppm')):
            m = re.search(rf'fb_(\d+)_w{w}', p)
            if m and (int(m.group(1)) in want if want else int(m.group(1)) >= int(vi0)):
                fr.append((int(m.group(1)), p))
        fr.sort()
        if not fr:
            print('no frames for', label); return 1
        pick = fr[:n]
        rows.append((label, [(v, load(p)) for v, p in pick]))
        print(label, 'frames', [v for v, _ in pick], 'of', len(fr))
    cw, pad, lab = 512, 6, 18
    imgs = []
    for label, fr in rows:
        cells = []
        for v, im in fr:
            sc = cw / im.width
            cells.append((f'{label} VI {v}', im.resize((cw, int(im.height * sc)), Image.NEAREST)))
        v, im = fr[0]
        crop = im.crop((cx, 0, im.width, 160))
        cells.append((f'{label} VI {v} radar box x{cx}..{im.width} (2x)', crop.resize((crop.width * 2, crop.height * 2), Image.NEAREST)))
        imgs.append(cells)
    W = max(sum(c.width + pad for _, c in r) for r in imgs) + pad
    H = sum(max(c.height for _, c in r) + lab + pad for r in imgs) + pad
    sheet = Image.new('RGB', (W, H), (40, 40, 40))
    dr = ImageDraw.Draw(sheet)
    y = pad
    for r in imgs:
        x = pad
        for t, c in r:
            dr.text((x, y), t, fill=(255, 255, 0))
            sheet.paste(c, (x, y + lab))
            x += c.width + pad
        y += max(c.height for _, c in r) + lab + pad
    sheet.save(out)
    print('wrote', out, sheet.size)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
