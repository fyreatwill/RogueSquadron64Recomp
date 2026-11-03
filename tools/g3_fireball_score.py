#!/usr/bin/env python3
"""s6811 G3: large-fireball / crash-flash comparison, retail angrylion fb dumps vs port window captures.

Both arms are aligned on their own flash frame (the brightest frame in the window: the destroyed-craft explosion washes
the whole screen), so no cross-arm clock is needed. Per frame: mean luma, mean RGB, and the fireball population
(hot pixels: R>=200, G>=120, B<=150, R>=B+70) with its mean colour. Each port frame is also paired with the retail frame
of best whole-frame match within +-PAIRWIN s of the same flash-relative time (d) and with the median retail frame
(control). Writes a side-by-side sheet (retail | port) of the paired frames around the flash.
usage: g3_fireball_score.py ORACLE_LOG PORT_DIR OUT.png [--t T0,T1 port window] [--rvi V0,V1 retail window] [--pairwin 0.4] [--scale 1]
s6811 lvl9 crash: --t 141,143.5 --rvi 13400,13700 --pairwin 0.2 --scale 2 over scratch/s6811/{pair/retail,burst/port}
"""
import glob, os, re, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g3_oracle_match as g
from PIL import Image, ImageStat

g.W, g.EXP = 512, [v << 3 for v in range(32)]
H = 446


def hot(p):
    return p[0] >= 200 and p[1] >= 120 and p[2] <= 150 and p[0] >= p[2] + 70


def stats(im):
    px = list(im.getdata())
    f = [p for p in px if hot(p)]
    m = ImageStat.Stat(im).mean
    fm = [round(sum(c[i] for c in f) / len(f)) for i in range(3)] if f else [0, 0, 0]
    return 0.299 * m[0] + 0.587 * m[1] + 0.114 * m[2], [round(x) for x in m], len(f), fm


def main():
    a = sys.argv[1:]
    log, pdir, out = a[0], a[1], a[2]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    t0, t1 = (float(v) for v in opt('--t', '0,1e9').split(','))
    pw = float(opt('--pairwin', '0.4'))
    sc = float(opt('--scale', '1'))  # retail s per port s: mupen 4 VI/tick vs port 2 VI/tick in flight -> 2 (s6805)
    v0, v1 = (int(v) for v in opt('--rvi', '0,99999999').split(','))  # retail VI window (keeps the respawn cut out)
    R = []
    for m in re.finditer(r'\[fb-dump\].*?start=0x([0-9a-f]+).*?vi0=(\d+) origin0=0x([0-9a-f]+) -> (\S+)', open(log).read()):
        st, vi, org, p = int(m[1], 16), int(m[2]), int(m[3], 16), m[4]
        base = org & ~0xFFF
        if not os.path.exists(p) or base - st < 0 or not v0 <= vi <= v1:
            continue
        raw = open(p, 'rb').read()
        if base - st + 512 * H * 2 > len(raw):
            continue
        R.append((vi / 60.0, g.decode(raw, base - st, H)))
    P = []
    for f in sorted(glob.glob(os.path.join(pdir, 'w_*.png'))):
        t = float(re.search(r'w_(\d+\.\d+)', f)[1])
        if t0 <= t <= t1:
            P.append((t, g.to_srgb(Image.open(f)).crop((85, 60, 1191, 1024)).resize((512, H), Image.BOX)))
    print(f'retail frames {len(R)}  port frames {len(P)}')
    if not R or not P:
        return
    arms = {}
    for name, fr in (('retail', R), ('port', P)):
        S = [(t, im) + stats(im) for t, im in fr]
        k = max(range(len(S)), key=lambda i: S[i][2])
        tf = S[k][0]
        arms[name] = [(x[0] - tf,) + x[1:] for x in S]
        print(f'== {name}: flash at {tf:.2f} s (luma {S[k][2]:.1f}, rgb {S[k][3]}), {len(S)} frames')
        print('   rel_s   luma  meanRGB          hot_px  hotRGB')
        for t, im, L, rgb, n, fm in arms[name]:
            if -0.5 <= t <= 1.2:
                print(f'  {t:+6.2f} {L:6.1f}  {str(rgb):16s} {n:6d}  {fm}')
    # pairs: port frame -> best retail frame within +-pw of the same flash-relative time; control = median d over all
    rs = [(t, g.small(im), im) for t, im, *_ in arms['retail']]
    rows = []
    for t, im, L, rgb, n, fm in arms['port']:
        if not -0.5 <= t <= 1.2:
            continue
        ps = g.small(im)
        ds = sorted((g.mad(ps, q), rt, rim) for rt, q, rim in rs)
        near = [x for x in ds if abs(x[1] - sc * t) <= pw]
        if not near:
            continue
        rows.append((t, near[0][0], near[0][1], ds[len(ds) // 2][0], im, near[0][2]))
        print(f'pair port {t:+6.2f} -> retail {near[0][1]:+6.2f}  d={near[0][0]:6.2f}  ctl median={ds[len(ds) // 2][0]:6.2f}')
    if rows:
        print(f'pairs {len(rows)}: median d {statistics.median(r[1] for r in rows):.2f}  '
              f'median ctl {statistics.median(r[3] for r in rows):.2f}')
        sh = Image.new('RGB', (512 * 2 // 2, H // 2 * len(rows)))
        for i, r in enumerate(rows):
            sh.paste(r[5].resize((256, H // 2)), (0, i * (H // 2)))
            sh.paste(r[4].resize((256, H // 2)), (256, i * (H // 2)))
        sh.save(out)


if __name__ == '__main__':
    main()
