#!/usr/bin/env python3
"""s6841 G3: find the abort-level "striped magenta/yellow terrain" frame (s6798 w133) in retail fb dumps or port captures.

Score = pixels of a 160x90 BOX resample with R>200, G<110, B>90 (s6840: 914 on s6798 w133, 0 on every other cap).
  g3_magenta_scan.py retail ORACLE_LOG [--w 512] [--h 446] [--sheet OUT.png]   (decodes each dump at its logged origin0)
  g3_magenta_scan.py port DIR [--sheet OUT.png]                                  (every *.png in DIR, window captures)
Prints one line per frame (time/vi, score) and a summary; --sheet writes a thumbnail strip of the top-scoring frames
plus their neighbours. --inject adds a positive control: each frame is scored again with a magenta block pasted over
1/8 of it, and the summary reports how many of those fired.
"""
import re, sys, os, glob, struct
from PIL import Image

def arg(k, d):
    return sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d

def score(im):
    s = im.convert('RGB').resize((160, 90), Image.BOX)
    return sum(1 for r, g, b in s.getdata() if r > 200 and g < 110 and b > 90)

def inject(im):
    im = im.convert('RGB').copy()
    w, h = im.size
    im.paste((230, 60, 160), (0, h // 2, w // 2, h // 2 + h // 4))
    return im

def retail_frames(log, W, H):
    for m in re.finditer(r'\[fb-dump\] t=\s*([\d.]+)s vi=(\d+) width=(\d+) origin=0x([0-9a-f]+) start=0x([0-9a-f]+) '
                         r'len=0x([0-9a-f]+).*?vi0=(\d+) origin0=0x([0-9a-f]+) -> (\S+)', open(log).read()):
        t, start, org, path = float(m[1]), int(m[5], 16), int(m[8], 16), m[9]
        raw = open(path, 'rb').read()
        off = (org & 0xFFFFFF) - start
        if off < 0 or off + W * H * 2 > len(raw):
            continue
        px = struct.unpack_from('>%dH' % (W * H), raw, off)
        out = bytearray(W * H * 3)
        for i, v in enumerate(px):
            out[3 * i], out[3 * i + 1], out[3 * i + 2] = ((v >> 11) & 31) << 3, ((v >> 6) & 31) << 3, ((v >> 1) & 31) << 3
        yield 't%.1f_vi%s' % (t, m[7]), Image.frombytes('RGB', (W, H), bytes(out))

def port_frames(d):
    for p in sorted(glob.glob(os.path.join(d, '*.png'))):
        im = Image.open(p)
        w, h = im.size
        yield os.path.basename(p), im.crop((0, min(64, h // 8), w, h))  # drop the window title bar

def main():
    mode, src = sys.argv[1], sys.argv[2]
    fr = retail_frames(src, int(arg('--w', 512)), int(arg('--h', 446))) if mode == 'retail' else port_frames(src)
    rows, inj = [], 0
    for name, im in fr:
        s = score(im)
        if '--inject' in sys.argv and score(inject(im)) > 150:
            inj += 1
        rows.append((name, s, im))
        print('%s %d' % (name, s))
    hits = [r for r in rows if r[1] > 150]
    print('SUMMARY frames=%d hits(>150)=%d max=%d inject_fired=%s' % (len(rows), len(hits), max([r[1] for r in rows] or [0]),
          inj if '--inject' in sys.argv else '-'))
    out = arg('--sheet', None)
    if out and rows:
        best = max(range(len(rows)), key=lambda i: rows[i][1])
        sel = rows[max(0, best - 3):best + 4]
        tw = 320
        th = int(tw * sel[0][2].size[1] / sel[0][2].size[0])
        sheet = Image.new('RGB', (tw * len(sel), th))
        for k, (_, _, im) in enumerate(sel):
            sheet.paste(im.convert('RGB').resize((tw, th)), (k * tw, 0))
        sheet.save(out)
        print('sheet', out, [r[0] for r in sel])

if __name__ == '__main__':
    main()
