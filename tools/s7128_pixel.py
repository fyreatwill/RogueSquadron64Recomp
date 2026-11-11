#!/usr/bin/env python3
"""s7128 wsheet-escape pixel check: for every W_SHEET_POS detection (DROPLOG.pos, 11th field = arm: 1 dropped, 0 kept by =t),
sample the hairline's path in the angrylion replay (hardware) and in the presented RT64 frame of the candidate swaps, plus a
parallel control path offset +-OFF px. Per fire, per swap: mean luminance on the line and off it, and mean |d| (RT64 vs AL).

  H-fixed : arm 1 line d ~ control d (RT64 == hardware where the wedge was dropped).
  H-harm  : arm 1 line d >> control d with AL brighter/different on the line (the wedge carried real pixels).
  Positive control (same run): arm 0 (kept) must show RT64 line darker than AL / line d >> control d, or the capture cannot see a
  hairline and an arm-1 null is worthless.

usage: s7128_pixel.py raw idx aldir pos.txt x0,y0,x1,y1 lag_ms [win_ms=40]
"""
import sys, os, bisect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import importlib.util
spec = importlib.util.spec_from_file_location('fid', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py'))
fid = importlib.util.module_from_spec(spec); spec.loader.exec_module(fid)

OFF = 6


def lum(p): return (p[0] * 3 + p[1] * 6 + p[2]) / 10.0


def main():
    rawp, idx, aldir, posp, rect = sys.argv[1:6]; lag = float(sys.argv[6]) * 24000; win = float(sys.argv[7] if len(sys.argv) > 7 else 40) * 24000
    rect = tuple(map(int, rect.split(','))); W, H = rect[2] - rect[0], rect[3] - rect[1]
    raw = fid.Raw(rawp); sw = {}
    for l in open(idx):
        p = l.split(); sw[int(p[0])] = int(p[1])
    have = {int(f[1:-4]) for f in os.listdir(aldir) if f.startswith('f') and f.endswith('.rgb')}
    ks = sorted(s for s in sw if s in have); kt = [sw[s] for s in ks]
    fires = []
    for l in open(posp):
        p = l.split()
        if len(p) < 11: continue
        fires.append((int(p[0]), [(float(p[1]), float(p[2])), (float(p[3]), float(p[4])), (float(p[5]), float(p[6]))], int(p[10])))
    cache = {}
    def AL(s):
        if ('a', s) not in cache:
            im = fid.load_al(os.path.join(aldir, 'f%d.rgb' % s)); cache[('a', s)] = (im.size, im.resize((W, H), Image.BOX))
        return cache[('a', s)]
    def P(i):
        if ('p', i) not in cache: cache[('p', i)] = raw.img(i).crop(rect)
        return cache[('p', i)]
    def at(m): return min(bisect.bisect_left(raw.T, m + lag), len(raw.T) - 1)
    print('fires', len(fires), 'arm1', sum(f[2] for f in fires), 'replayed swaps', len(ks))
    print('tick arm swap dt_ms npts | AL_line AL_ctl RT_line RT_ctl | d_line d_ctl | verdict')
    summ = {0: [], 1: []}
    for t, v, arm in fires:
        # corner = the vertex farthest from the other two; base = midpoint of the other two
        best = None
        for i in range(3):
            o = [v[j] for j in range(3) if j != i]
            dd = sum(((v[i][0] - q[0]) ** 2 + (v[i][1] - q[1]) ** 2) for q in o)
            if best is None or dd > best[0]: best = (dd, v[i], ((o[0][0] + o[1][0]) / 2, (o[0][1] + o[1][1]) / 2))
        _, c, b = best
        lo = bisect.bisect_left(kt, t - win); hi = bisect.bisect_right(kt, t + 2 * 24000)
        rows = []
        for k in range(lo, hi):
            s = ks[k]; (aw, ah), a = AL(s); sx, sy = W / aw, H / ah
            i0 = at(sw[s]); cand = [(fid.dmap(a, P(j)), j) for j in range(max(0, i0 - 2), min(len(raw.T), i0 + 3))]
            dm, j = min(((sum(d) / len(d), j) for d, j in cand)); p = P(j); d = fid.dmap(a, p)
            ln, ct = [], []
            n = 400
            dx, dy = b[0] - c[0], b[1] - c[1]; L = (dx * dx + dy * dy) ** .5; nx, ny = -dy / L, dx / L
            for q in range(n):
                f = q / n; x, y = c[0] + dx * f, c[1] + dy * f
                if not (0 <= x < aw and 0 <= y < ah): continue
                X, Y = int(x * sx), int(y * sy)
                if not (0 <= X < W and 0 <= Y < H): continue
                ln.append((X, Y))
                for sgn in (1, -1):
                    X2, Y2 = int((x + sgn * OFF * nx) * sx), int((y + sgn * OFF * ny) * sy)
                    if 0 <= X2 < W and 0 <= Y2 < H: ct.append((X2, Y2))
            ln = list(dict.fromkeys(ln)); ct = list(dict.fromkeys(ct))
            if len(ln) < 10 or not ct: continue
            m = lambda im, pts: sum(lum(im.getpixel(z)) for z in pts) / len(pts)
            md = lambda pts: sum(d[y * W + x] for x, y in pts) / len(pts)
            r = (s, (sw[s] - t) / 24000, len(ln), m(a, ln), m(a, ct), m(p, ln), m(p, ct), md(ln), md(ct))
            rows.append(r)
        if not rows:
            print(t, arm, 'no replayed swap in window'); continue
        # the owning swap: largest line-vs-control |d| excess (for arm 0 that is where the hairline is drawn)
        own = max(rows, key=lambda r: r[7] - r[8])
        for r in rows:
            tag = '*' if r is own else ' '
            print('%d %d %s%d %+.1f %d | %.0f %.0f %.0f %.0f | %.1f %.1f' % ((t, arm, tag) + r))
        summ[arm].append(own)
    for arm in (0, 1):
        o = summ[arm]
        if not o: print('arm', arm, 'n=0'); continue
        ex = sorted(r[7] - r[8] for r in o); dk = sorted((r[6] - r[5]) - (r[4] - r[3]) for r in o)
        print('arm %d n=%d line-minus-ctl d: median %.1f max %.1f | RT darkening beyond AL (ctl-line): median %.1f max %.1f' %
              (arm, len(o), ex[len(ex) // 2], ex[-1], dk[len(dk) // 2], dk[-1]))


if __name__ == '__main__':
    main()
