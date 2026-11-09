#!/usr/bin/env python3
"""s7032: frozen-pose scorer for cull arms from tools/g3_optin_pose_arms.sh (f{k}_{1,2}.png per arm).
Per freeze k: mean |dLum| (0-255) and fraction of pixels off by > THR of each arm vs the base arm; base vs its own
second capture (intra-freeze floor, should be ~0) and offB vs offA (cross-run A/A floor). A cull is invisible at a pose
when its score sits at the A/A floor while the positive-control arm sits well above it.
Usage: s7032_pose_cull_score.py DIR [--base offA] [--aa offB] [--sheet out.jpg]"""
import os, sys, glob
from PIL import Image, ImageChops, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_oracle_match import to_srgb
THR = 24

def load(d, arm, k, i=1):
    p = os.path.join(d, arm, 'f%d_%d.png' % (k, i))
    return to_srgb(Image.open(p)).convert('L') if os.path.exists(p) else None

def score(a, b):
    if a is None or b is None: return None
    if a.size != b.size: b = b.resize(a.size)
    h = ImageChops.difference(a, b).histogram(); n = sum(h)
    return sum(i * c for i, c in enumerate(h)) / n, sum(h[THR + 1:]) / n

def main():
    a = sys.argv[2:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    d, base, aa = sys.argv[1], opt('--base', 'offA'), opt('--aa', 'offB')
    arms = sorted(n for n in os.listdir(d) if glob.glob(os.path.join(d, n, 'f*_1.png')))
    ks = sorted(int(os.path.basename(p)[1:].split('_')[0]) for p in glob.glob(os.path.join(d, base, 'f*_1.png')))
    others = [x for x in arms if x != base]
    print('k  intra(%s) ' % base + ' '.join('%-16s' % x for x in others))
    for k in ks:
        b = load(d, base, k); row = []
        s = score(b, load(d, base, k, 2)); row.append('%5.2f/%.3f' % s if s else '  -  ')
        for x in others:
            s = score(b, load(d, x, k)); row.append(('%6.2f/%.3f' % s if s else '-').ljust(16))
        print('%d  %s  %s' % (k, row[0], ' '.join(row[1:])))
    if '--sheet' in a:
        show = [x for x in [base] + opt('--show', 'r2,k03').split(',') if x in arms]; W = 480
        rows = []
        for k in ks:
            b = load(d, base, k)
            if b is None: continue
            ims = [to_srgb(Image.open(os.path.join(d, x, 'f%d_1.png' % k))).convert('RGB') for x in show if os.path.exists(os.path.join(d, x, 'f%d_1.png' % k))]
            for x in show[1:]:
                o = load(d, x, k)
                if o is not None: ims.append(ImageOps.autocontrast(ImageChops.difference(b, o.resize(b.size))).convert('RGB'))
            ims = [im.resize((W, int(im.height * W / im.width))) for im in ims]; rows.append(ims)
        H = rows[0][0].height; cols = max(len(r) for r in rows)
        sh = Image.new('RGB', (W * cols, H * len(rows)))
        for j, r in enumerate(rows):
            for i, im in enumerate(r): sh.paste(im, (i * W, j * H))
        sh.save(opt('--sheet', 'sheet.jpg'), quality=85)
        print('sheet cols:', show + ['|%s-%s| (autocontrast)' % (x, base) for x in show[1:]])

main()
