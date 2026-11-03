#!/usr/bin/env python3
"""s6812 G3: tick-keyed pairing of retail angrylion fb dumps and port window captures (multi-event windows).

g3_fireball_score.py aligns each arm on its single brightest frame; a cutscene with several explosions has no single
flash, so this pairs frames by SIM TICK instead (dt pinned, sim identical across arms, s6767-style snap.txt map).
  retail dump vi0 -> tick via snap.txt retail VI column
  port capture wall t -> port VI = (t - t0)*60 -> tick via snap.txt port VI column; t0 = median over captures of
  (t - pvi(best free-search retail match)/60), keeping only matches with d < --fitd (scene cuts make these unambiguous)
Per pair: d = mean abs diff (g3_oracle_match.small/mad) to the retail dump(s) within +-TW ticks, control = median d to
all retail dumps; plus hot-pixel population (g3_fireball_score.hot) per frame. Writes a retail|port sheet.
usage: g3_tick_pair_score.py ORACLE_LOG PORT_DIR SNAP_TXT OUT.png [--ticks A,B] [--tw 1] [--fitd 6] [--t0 T]
"""
import bisect, glob, os, re, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g3_oracle_match as g
from g3_fireball_score import H, stats
from PIL import Image

g.W, g.EXP = 512, [v << 3 for v in range(32)]


def main():
    a = sys.argv[1:]
    log, pdir, snap, out = a[:4]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    k0, k1 = (int(v) for v in opt('--ticks', '0,99999999').split(','))
    tw, fitd = int(opt('--tw', '1')), float(opt('--fitd', '6'))
    T = [tuple(map(int, m.groups())) for m in (re.match(r'tick\s+(\d+) \S+ vi (\d+)/(\d+)', l) for l in open(snap)) if m]
    rv, pv = [t[1] for t in T], [t[2] for t in T]
    tick_r = lambda v: T[bisect.bisect_right(rv, v) - 1][0] if rv[0] <= v <= rv[-1] else None
    tick_p = lambda v: T[bisect.bisect_right(pv, v) - 1][0] if pv[0] <= v <= pv[-1] else None
    pvi = {t[0]: t[2] for t in T}
    R = []
    for m in re.finditer(r'\[fb-dump\].*?start=0x([0-9a-f]+).*?vi0=(\d+) origin0=0x([0-9a-f]+) -> (\S+)', open(log).read()):
        st, vi, org, p = int(m[1], 16), int(m[2]), int(m[3], 16), m[4]
        base, k = org & ~0xFFF, tick_r(int(m[2]))
        if not os.path.exists(p) or base - st < 0 or k is None:
            continue
        raw = open(p, 'rb').read()
        if base - st + 512 * H * 2 > len(raw):
            continue
        im = g.decode(raw, base - st, H)
        R.append((k, vi, im, g.small(im)) + stats(im))
    P = []
    for f in sorted(glob.glob(os.path.join(pdir, 'w_*.png'))):
        t = float(re.search(r'w_(\d+\.\d+)', f)[1])
        im = g.to_srgb(Image.open(f)).crop((85, 60, 1191, 1024)).resize((512, H), Image.BOX)
        P.append((t, im, g.small(im)))
    print(f'retail dumps {len(R)} (ticks {R[0][0] if R else "-"}-{R[-1][0] if R else "-"})  port caps {len(P)}')
    if not R or not P:
        return
    if '--t0' in a:
        t0 = float(opt('--t0', '0'))
    else:
        fits = []
        for t, im, s in P:
            d, k = min((g.mad(s, r[3]), r[0]) for r in R)
            if d < fitd:
                fits.append(t - pvi[k] / 60)
        t0 = statistics.median(fits)
        print(f't0 = {t0:.3f} s from {len(fits)} free-search fits (spread p25-p75 '
              f'{statistics.quantiles(fits, n=4)[0]:.2f}..{statistics.quantiles(fits, n=4)[2]:.2f})' if len(fits) > 3 else
              f't0 = {t0:.3f} from {len(fits)} fits')
    rows = []
    for t, im, s in P:
        k = tick_p(round((t - t0) * 60))
        if k is None or not k0 <= k <= k1:
            continue
        near = [r for r in R if abs(r[0] - k) <= tw]
        if not near:
            continue
        ds = sorted(g.mad(s, r[3]) for r in R)
        d, r = min(((g.mad(s, r[3]), r) for r in near), key=lambda x: x[0])
        L, rgb, n, fm = stats(im)
        rows.append((k, t, d, ds[len(ds) // 2], ds[0], r, im, n, fm))
    print('  tick  port_s   d     ctl   best  | retail vi hot_px hotRGB      | port hot_px hotRGB')
    for k, t, d, c, b, r, im, n, fm in rows:
        print(f'{k:6d} {t:7.2f} {d:6.2f} {c:6.2f} {b:6.2f} | {r[1]:6d} {r[6]:6d} {str(r[7]):14s}| {n:6d} {fm}')
    if not rows:
        return
    print(f'pairs {len(rows)}: median d {statistics.median(x[2] for x in rows):.2f}  '
          f'median ctl {statistics.median(x[3] for x in rows):.2f}  pairs with d<=best+1: '
          f'{sum(x[2] <= x[4] + 1 for x in rows)}')
    sh = Image.new('RGB', (512, H // 2 * len(rows)))
    for i, x in enumerate(rows):
        sh.paste(x[5][2].resize((256, H // 2)), (0, i * (H // 2)))
        sh.paste(x[6].resize((256, H // 2)), (256, i * (H // 2)))
    sh.save(out)


if __name__ == '__main__':
    main()
