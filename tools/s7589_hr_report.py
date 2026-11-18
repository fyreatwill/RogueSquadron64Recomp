#!/usr/bin/env python3
"""s7589 class HR scorer. usage: s7589_hr_report.py <hr.tsv> --warm S --plant-at S [--plant-every 30] [--log run.log]
Least-squares slope (per minute) of every column in the game-only window [warm, plant_at) and the plant window [plant_at, end].
Control PASS when fds/threads/ports each rise by >= 0.7 x the planted rate (60/every per min) more in the plant window than in the
game-only window. Verdict: game-only |slope| <= 0.2/min (fd/thr/port) and <= 0.2/min IOSurface regions -> flat. rc 0 flat+ctl, 1 growth, 3 ctl FAIL."""
import sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument('tsv'); ap.add_argument('--warm', type=float, default=120)
ap.add_argument('--plant-at', type=float, default=1e18); ap.add_argument('--plant-every', type=float, default=30); ap.add_argument('--log')
ap.add_argument('--windows', help='a-b,c-d,...: median of each column per window (plateaus between loads)')
a = ap.parse_args()
rows = [l.rstrip('\n').split('\t') for l in open(a.tsv)]; hdr = rows[0]; data = []
for r in rows[1:]:
    try: data.append([float(x) if x not in ('na', '') else None for x in r])
    except ValueError: pass
def slope(pts):
    pts = [(t, v) for t, v in pts if v is not None]
    if len(pts) < 3: return None
    n = len(pts); mt = sum(t for t, _ in pts) / n; mv = sum(v for _, v in pts) / n
    d = sum((t - mt) ** 2 for t, _ in pts); return 60 * sum((t - mt) * (v - mv) for t, v in pts) / d if d else None
f = lambda x: 'na' if x is None else f'{x:+.3f}'
res = {}
print(f"{'col':12s} {'first':>8s} {'max':>8s} {'last':>8s} {'game/min':>9s} {'plant/min':>9s}")
for i, c in enumerate(hdr[1:], 1):
    g = [(r[0], r[i]) for r in data if a.warm <= r[0] < a.plant_at]; p = [(r[0], r[i]) for r in data if r[0] >= a.plant_at]
    vals = [r[i] for r in data if r[i] is not None]; sg, sp = slope(g), slope(p); res[c] = (sg, sp)
    print(f"{c:12s} {vals[0] if vals else 'na':>8} {max(vals) if vals else 'na':>8} {vals[-1] if vals else 'na':>8} {f(sg):>9s} {f(sp):>9s}")
if a.windows:
    import statistics
    ws = [tuple(map(float, w.split('-'))) for w in a.windows.split(',')]
    print('plateaus (median per window):', ' | '.join(f'{lo:.0f}-{hi:.0f}' for lo, hi in ws))
    for i, c in enumerate(hdr[1:], 1):
        med = []
        for lo, hi in ws:
            v = [r[i] for r in data if lo <= r[0] < hi and r[i] is not None]; med.append(statistics.median(v) if v else None)
        steps = [None if x is None or y is None else y - x for x, y in zip(med, med[1:])]
        print(f"  {c:12s} " + ' '.join('na' if m is None else f'{m:g}' for m in med) + '   steps ' + ' '.join('na' if d is None else f'{d:+g}' for d in steps))
rate = 60 / a.plant_every; ctl = True; key = ('fds', 'threads', 'ports')
if a.plant_at < 1e17:
    for c in key:
        sg, sp = res.get(c, (None, None)); ok = sg is not None and sp is not None and sp - sg >= 0.7 * rate
        ctl &= ok; print(f"ctl {c}: plant-game {f(None if sp is None or sg is None else sp - sg)} vs need {0.7*rate:.2f} -> {'PASS' if ok else 'FAIL'}")
else: ctl = False; print('ctl: no plant window -> FAIL')
if a.log:
    n = sum(1 for l in open(a.log, errors='replace') if '[s7589-hrplant] n=' in l); print(f'plant banners in log: {n}')
grow = [c for c in key + ('iosurf_n', 'ioaccel_g_n') if res.get(c, (None,))[0] is not None and abs(res[c][0]) > 0.2]
print('verdict:', 'CTL FAIL' if not ctl else ('GROWTH ' + ','.join(grow) if grow else 'FLAT (H-flat)'))
sys.exit(3 if not ctl else (1 if grow else 0))
