#!/usr/bin/env python3
"""s6746 G3: population statistic for short-lived effects (laser bolts) that per-frame oracle matching cannot pair.

A bolt lives a few frames, and a port window capture lands up to ~0.12 s off the retail dump phase, so retail-vs-port
pairs disagree on bolt presence frame by frame. Compare instead the fraction of frames carrying effect pixels per arm.
Counts pixels with R>RMIN, G<GMAX, B<GMAX inside BOX (512x446 frame coords; default = band above the craft, excludes the
radar and engine glows) and prints per arm: frames, % frames >=4 / >=15 px, mean count, and mean RGB of those pixels.
Usage:
  g3_effect_count.py [--retail LOG]... [--port DIR]... [--t T0,T1] [--box X0,Y0,X1,Y1] [--rmin 170] [--gmax 80]
    --retail: rs64_oracle log with 512-wide --fb-dump lines (bases 690000/620000, shift decode, black frames skipped)
    --port:   g3_port_capture.sh dir (w_<secs>.png, picture box x 85..1191 y 60..1024 of the 1280x1024 window)
"""
import sys, re, glob, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g3_oracle_match as g
from PIL import Image

def main():
    a = sys.argv[1:]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    many = lambda k: [a[i + 1] for i, x in enumerate(a) if x == k]
    box = tuple(int(v) for v in opt('--box', '60,150,450,226').split(','))
    t0, t1 = (float(v) for v in opt('--t', '0,1e9').split(','))
    rmin, gmax = int(opt('--rmin', '170')), int(opt('--gmax', '80'))
    g.W = 512; g.EXP = [v << 3 for v in range(32)]
    def frames_retail(log):
        for m in re.finditer(r'\[fb-dump\].*?start=0x([0-9a-f]+).*?vi0=(\d+) origin0=0x([0-9a-f]+) -> (\S+)', open(log).read()):
            st, org, p = int(m[1], 16), int(m[3], 16), m[4]
            base = next((b for b in (0x690000, 0x620000) if 0 <= org - b <= 0x500 + 2048), None)
            if base is None or not os.path.exists(p):
                continue
            im = g.decode(open(p, 'rb').read(), base - st, 446)
            if sum(im.convert('L').resize((32, 28)).getdata()) / 896 >= 60:
                yield im
    def frames_port(d):
        for f in sorted(glob.glob(os.path.join(d, 'w_*.png'))):
            if t0 <= float(re.search(r'w_(\d+\.\d+)', f)[1]) <= t1:
                yield g.to_srgb(Image.open(f)).crop((85, 60, 1191, 1024)).resize((512, 446), Image.BOX)
    arms = [('retail ' + l, frames_retail(l)) for l in many('--retail')] + [('port ' + d, frames_port(d)) for d in many('--port')]
    for name, it in arms:
        cs, acc, npx = [], [0, 0, 0], 0
        for im in it:
            c = 0
            for p in im.crop(box).getdata():
                if p[0] > rmin and p[1] < gmax and p[2] < gmax:
                    c += 1; npx += 1; acc = [x + y for x, y in zip(acc, p)]
            cs.append(c)
        n = max(len(cs), 1)
        print('%s\n  n=%d  >=4px %.1f%%  >=15px %.1f%%  mean %.1f  max %d  rgb %s' % (name, len(cs), 100 * sum(c >= 4 for c in cs) / n,
              100 * sum(c >= 15 for c in cs) / n, sum(cs) / n, max(cs or [0]), [round(x / max(npx, 1), 1) for x in acc]))

if __name__ == '__main__':
    main()
