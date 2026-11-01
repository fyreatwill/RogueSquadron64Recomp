#!/usr/bin/env python3
"""s6761 G3: HUD presence per frame, retail fb dumps vs port window captures, keyed by sim tick.
Score = fraction of radar-ring red pixels (R>150, G<70, B<70) in the 512x446 frame box (385,25)-(480,140).
Port capture time -> port VI via t0 (median of best-match pairs in match.txt), port VI -> tick via snap.txt.
Prints every port HUD-off run (score < 0.05 for >= 3 captures) with its tick range, and the retail dumps whose tick
falls inside it.
usage: g3_hud_presence.py SDIR  (needs SDIR/retail/oracle.log, SDIR/port/w_*.png, SDIR/snap.txt, SDIR/match.txt)"""
import bisect, glob, os, re, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g3_oracle_match as g
from PIL import Image

g.W, g.EXP = 512, [v << 3 for v in range(32)]


def red(im):
    px = list(im.crop((385, 25, 480, 140)).getdata())
    return sum(1 for r, gg, b in px if r > 150 and gg < 70 and b < 70) / len(px)


def main():
    S = sys.argv[1]
    T = [tuple(map(int, m.groups())) for m in (re.match(r'tick\s+(\d+) \S+ vi (\d+)/(\d+)', l) for l in open(S + '/snap.txt')) if m]
    rv, pv = [t[1] for t in T], [t[2] for t in T]
    tick_r = lambda v: T[bisect.bisect_right(rv, v) - 1][0] if rv[0] <= v <= rv[-1] else None
    tick_p = lambda v: T[bisect.bisect_right(pv, v) - 1][0] if pv[0] <= v <= pv[-1] else None
    t0s = []
    for l in open(S + '/match.txt'):
        m = re.search(r'retail vi=\s*(\d+).*port n=\s*(\d+) d=\s*([\d.]+)', l)
        if m and float(m[3]) < 6 and tick_r(int(m[1])) is not None:
            k = tick_r(int(m[1])); t0s.append(int(m[2]) / 100 - T[k][2] / 60)
    t0 = statistics.median(t0s)
    print(f'ticks {len(T)}  t0={t0:.2f}s from {len(t0s)} pairs')
    retail = []
    for m in re.finditer(r'\[fb-dump\].*?start=0x([0-9a-f]+) len=0x([0-9a-f]+).*?vi0=(\d+) origin0=0x([0-9a-f]+) -> (\S+)',
                         open(S + '/retail/oracle.log').read()):
        start, vi0, org, path = int(m[1], 16), int(m[3]), int(m[4], 16), m[5]
        base = next((b for b in (0x690000, 0x620000) if 0 <= org - b <= 0x500 + 2048), None)
        if base is None or not os.path.exists(path) or tick_r(vi0) is None:
            continue
        retail.append((tick_r(vi0), vi0, red(g.decode(open(path, 'rb').read(), base - start, 446))))
    port = []
    for f in sorted(glob.glob(S + '/port/w_*.png')):
        t = float(re.search(r'w_(\d+\.\d+)', f)[1]); k = tick_p(round((t - t0) * 60))
        if k is not None:
            port.append((k, t, red(g.to_srgb(Image.open(f)).crop((85, 60, 1191, 1024)).resize((512, 446), Image.BOX))))
    print('retail HUD on %d/%d dumps in tick range' % (sum(r[2] >= 0.05 for r in retail), len(retail)))
    print('port   HUD on %d/%d captures in tick range' % (sum(p[2] >= 0.05 for p in port), len(port)))
    runs, cur = [], []
    for p in port + [(None, None, 1)]:
        if p[2] < 0.05:
            cur.append(p)
        else:
            if len(cur) >= 3:
                runs.append(cur)
            cur = []
    for r in runs:
        a, b = r[0][0], r[-1][0]
        inside = [x for x in retail if a <= x[0] <= b]
        print(f'port HUD-off ticks {a}-{b} ({r[0][1]:.1f}-{r[-1][1]:.1f}s, {len(r)} caps); retail dumps inside: ' +
              (' '.join(f't{x[0]}/vi{x[1]}:{"on" if x[2] >= 0.05 else "off"}' for x in inside) or 'none'))


if __name__ == '__main__':
    main()
