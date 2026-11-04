#!/usr/bin/env python3
"""s6872 G3: score same-pose opt-in arms (tools/g3_optin_pose_arms.sh) against a dd1 baseline, window PNGs, P3 -> sRGB.

Frozen frames are compared one to one per freeze k, so no median and no phase search. Ground = pixels the baseline draws as
terrain or craft (not blue sky or white cloud). Reports, per arm and k: mean |dLum| over ground, fraction of ground off by > THR,
and the fraction of the baseline's sky that became non-sky (the far terrain an opt-in is meant to add). dd1b = cross-run noise
floor, shift = positive control. Usage: g3_optin_diff.py ARMS_DIR [--base dd1a] [--out sheet.png]"""
import os, sys, glob
from PIL import Image, ImageChops
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_oracle_match import to_srgb
THR = 24

def load(root, arm, k):
    p = os.path.join(root, arm, 'f%d_1.png' % k)
    return to_srgb(Image.open(p)) if os.path.exists(p) else None

def sky(p):
    return p[2] > max(p[0], p[1]) + 8 or min(p) > 170

def main():
    a = sys.argv[2:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    root, base = sys.argv[1], opt('--base', 'dd1a')
    arms = sorted(n for n in os.listdir(root) if glob.glob(os.path.join(root, n, 'f*_1.png')))
    ks = sorted(int(os.path.basename(p)[1]) for p in glob.glob(os.path.join(root, base, 'f*_1.png')))
    print('%-10s %2s %8s %8s %8s' % ('arm', 'k', 'gnd_mad', 'gnd>T', 'sky_new'))
    rows = []
    for n in arms:
        for k in ks:
            b, m = load(root, base, k), load(root, n, k)
            if m is None or m.size != b.size: print(n, k, 'missing or size differs'); continue
            bp, mp = list(b.getdata()), list(m.getdata())
            bl, ml = list(b.convert('L').getdata()), list(m.convert('L').getdata())
            d = [abs(x - y) for x, y, p in zip(bl, ml, bp) if not sky(p) and sum(p) > 12]
            sk = [q for p, q in zip(bp, mp) if sky(p)]
            new = sum(not sky(q) for q in sk) / max(len(sk), 1)
            print('%-10s %2d %8.2f %8.4f %8.4f' % (n, k, sum(d) / max(len(d), 1), sum(x > THR for x in d) / max(len(d), 1), new))
            rows.append((n, k, m, b))
    if '--out' in a:
        W, H = 320, 256; sh = Image.new('RGB', (W * 2 * len(ks), H * len(arms)))
        for n, k, m, b in rows:
            y = arms.index(n) * H; x = ks.index(k) * 2 * W
            sh.paste(m.resize((W, H)), (x, y))
            sh.paste(ImageChops.difference(m, b).point(lambda v: min(255, v * 4)).resize((W, H)), (x + W, y))
        sh.save(opt('--out', ''))

if __name__ == '__main__': main()
