#!/usr/bin/env python3
"""s6738 G3: match retail (rs64_oracle --fb-dump, angrylion RDRAM) frames to port (ROGUESQ_FB_DUMP_DIR ppm) frames.

Pure PIL (no numpy on this host). Retail dumps are raw big-endian RDRAM windows; the displayed buffer is decoded at
the base whose VI origin0 the oracle logged (origin = base + 0x500, + one 1280-byte row on interlace field 1). Each
retail frame is matched to the port frame with min mean |dLum| on a 160x84 grid; the best pairs are written as
retail | port | 16x16-tile |dLum| heat map (x4). Usage:
  g3_oracle_match.py ORACLE_LOG PORT_DIR OUT_DIR [--bases 695C00,62B800] [--h 336] [--min-vi N] [--win Y0,Y1] [--winx X0,X1] [--w 512] [--dec full|shift] [--fitd 6]
--win: PORT_DIR holds window captures (w_<secs>.png, s6738 port_win.sh); rows Y0..Y1 are the letterboxed VI picture
(1280x1024 Retina 640x480 window, 640x336 VI: 208,880). RDRAM ppm dumps are NOT valid for 3D scenes: RT64 renders on
the GPU and does not write those frames back (s6738: port RDRAM held the stale N64 logo through the cinematic).
"""
import re, sys, os, glob, struct, io
from PIL import Image, ImageChops, ImageStat, ImageCms

W = 640
# s6744: 5->8 bit expansion. 'full' = v*255/31 (default before s6744); 'shift' = v<<3, the unbiased inverse of the RDP's
# dither-then-truncate (sum over dither 0..7 of floor((x+d)/8) = x) and what the VI DAC path does.
EXP = [v * 255 // 31 for v in range(32)]

def linfit(xs, ys):
    n = len(xs); mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs); sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    a = sxy / sxx if sxx else 0.0
    return a, my - a * mx

def decode(raw, off, h):
    px = struct.unpack_from('>%dH' % (W * h), raw, off)
    out = bytearray(W * h * 3)
    for i, v in enumerate(px):
        out[3 * i] = EXP[(v >> 11) & 31]
        out[3 * i + 1] = EXP[(v >> 6) & 31]
        out[3 * i + 2] = EXP[(v >> 1) & 31]
    return Image.frombytes('RGB', (W, h), bytes(out))

_SRGB = ImageCms.createProfile('sRGB')

def to_srgb(im):
    # s6740: macOS screencapture tags window PNGs with the Display P3 profile, so their raw values are P3-encoded
    # (sRGB colours read desaturated: blue sky R+8/G-8, dark channels +19). Retail RDRAM decodes are plain sRGB-ish
    # 5551, so convert captures to sRGB before any pixel diff. --no-icc keeps the raw values.
    icc = im.info.get('icc_profile')
    if not icc or '--no-icc' in sys.argv:
        return im.convert('RGB')
    return ImageCms.profileToProfile(im.convert('RGB'), ImageCms.ImageCmsProfile(io.BytesIO(icc)), _SRGB,
                                     renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC)

def small(im):
    return im.convert('L').resize((160, 84), Image.BOX)

def mad(a, b):
    return ImageStat.Stat(ImageChops.difference(a, b)).mean[0]

def main():
    log, pdir, out = sys.argv[1:4]
    a = sys.argv[4:]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    global W, EXP
    if opt('--dec', 'full') == 'shift':
        EXP = [v << 3 for v in range(32)]
    W = int(opt('--w', '640'))  # s6739: 512 for the attract-demo flight (bases 690000,620000)
    bases = [int(x, 16) for x in opt('--bases', '695C00,62B800').split(',')]
    H, minvi = int(opt('--h', '336')), int(opt('--min-vi', '0'))
    os.makedirs(out, exist_ok=True)
    retail = []
    for m in re.finditer(r'\[fb-dump\].*?start=0x([0-9a-f]+) len=0x([0-9a-f]+).*?vi0=(\d+) origin0=0x([0-9a-f]+) -> (\S+)', open(log).read()):
        start, vi0, org, path = int(m[1], 16), int(m[3]), int(m[4], 16), m[5]
        base = next((b for b in bases if 0 <= org - b <= 0x500 + 2 * W * 2), None)
        if base is None or vi0 < minvi or not os.path.exists(path):
            continue
        raw = open(path, 'rb').read()
        if base - start < 0 or base - start + W * H * 2 > len(raw):
            continue
        retail.append((vi0, org, decode(raw, base - start, H)))
    port = []
    if '--win' in a:
        y0, y1 = (int(v) for v in opt('--win', '208,880').split(','))
        for f in sorted(glob.glob(os.path.join(pdir, 'w_*.png'))):
            im = to_srgb(Image.open(f))
            x0, x1 = (int(v) for v in opt('--winx', '0,%d' % im.size[0]).split(','))  # s6739: pillar-boxed 512 VI
            port.append((int(float(re.search(r'w_(\d+\.\d+)', f)[1]) * 100), im.crop((x0, y0, x1, y1)).resize((W, H), Image.BOX)))
    for f in sorted(glob.glob(os.path.join(pdir, 'fb_*_w640.ppm'))):
        im = Image.open(f).convert('RGB')
        if im.size[1] >= H:
            port.append((int(re.search(r'fb_(\d+)', f)[1]), im.crop((0, 0, W, H))))
    print(f'retail frames {len(retail)}  port frames {len(port)}')
    if not retail or not port:
        return
    ps = [small(p[1]) for p in port]
    rows = []
    for vi0, org, r in retail:
        rs = small(r)
        d = sorted((mad(rs, q), k) for k, q in enumerate(ps))
        meanL = ImageStat.Stat(rs).mean[0]
        rows.append((d[0][0], vi0, d[0][1], meanL, r))
        print(f'retail vi={vi0:5d} org={org:06x} meanL={meanL:6.1f} -> port n={port[d[0][1]][0]:5d} d={d[0][0]:6.2f} '
              f'2nd={d[1][0] if len(d) > 1 else -1:6.2f} median={d[len(d) // 2][0]:6.2f}')
    rows = sorted([r for r in rows if r[3] > 8], key=lambda r: r[0])
    # s6744: per-channel fit retail = a*port + b over 16x16 block means of the best pairs (d < --fitd, default 6), so a
    # multiplicative gain (a != 1, b ~ 0) separates from an offset (a ~ 1, b != 0).
    fx = [[], [], []]; fy = [[], [], []]
    for dv, vi0, k, _, r in rows[:12]:
        if dv >= float(opt('--fitd', '6')):
            continue
        rb, pb = r.resize((W // 16, H // 16), Image.BOX), port[k][1].resize((W // 16, H // 16), Image.BOX)
        for c in range(3):
            fx[c] += list(pb.getchannel(c).tobytes()); fy[c] += list(rb.getchannel(c).tobytes())
    if fx[0]:
        print('fit retail=a*port+b (%d blocks, dec=%s): ' % (len(fx[0]), opt('--dec', 'full')) +
              '  '.join('%s a=%.4f b=%+.2f' % ((ch,) + linfit(fx[c], fy[c])) for c, ch in enumerate('RGB')))
    for rank, (dv, vi0, k, _, r) in enumerate(rows[:6]):
        p = port[k][1]
        diff = ImageChops.difference(r.convert('L'), p.convert('L'))
        t = diff.resize((W // 16, H // 16), Image.BOX)
        tv = list(t.tobytes())
        heat = Image.merge('RGB', [t.point(lambda v: min(255, v * 4)).resize((W // 16 * 16, H // 16 * 16), Image.NEAREST),
                                   Image.new('L', (W // 16 * 16, H // 16 * 16)), Image.new('L', (W // 16 * 16, H // 16 * 16))])
        sheet = Image.new('RGB', (W * 3, H)); sheet.paste(r, (0, 0)); sheet.paste(p, (W, 0)); sheet.paste(heat, (2 * W, 0))
        sheet.save(os.path.join(out, f'pair{rank}_vi{vi0}_n{port[k][0]}.png'))
        rm, pm = ImageStat.Stat(r).mean, ImageStat.Stat(p).mean
        print(f'pair{rank}: vi={vi0} n={port[k][0]} d={dv:.2f} tiles>8={sum(v > 8 for v in tv)}/{len(tv)} '
              f'tiles>40={sum(v > 40 for v in tv)} max_tile={max(tv)} meanRGB retail={[round(x,1) for x in rm]} port={[round(x,1) for x in pm]}')

if __name__ == '__main__':
    main()
