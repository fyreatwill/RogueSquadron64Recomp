#!/usr/bin/env python3
"""s7768: why does an FPS60 flight run drop from 60 to ~30 game frames/s? Joins per-VI [g3c] lines (ROGUESQ_G3C_LOG=1:
arbiter limit byte lim, gfx task count, player pos) with per-second [g1b]/[g1b-gt] lines (ROGUESQ_G1B=1) per 5 s window.
usage: s7768_fps60_rate.py <log> [win_s=5]
Per window: VIs, tasks/s (new game frames), lim histogram, player path/s, send_dl wall avg, guest-thread cpu (g1b-gt).
Verdict per slow window (tasks/s < 45 with >= 250 VIs): H-limit if lim!=1 on >50% of VIs, elif send_dl wall avg > 13 ms H-cost (gfx task near/over the 16.7 ms VI budget), else H-other."""
import re, sys, collections
p = sys.argv[1]; W = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
g3 = re.compile(r'^\[g3c\] vi=(\d+) t=([\d.]+) tasks=(\d+) lim=(-?\d+) .* pl=([-\deE.+na,]+)')
g1 = re.compile(r'^\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+) sd_wall=([\d.]+)/(\d+) sd_cpu=([\d.]+)/(\d+)')
gt = re.compile(r'^\[g1b-gt\] t=(\d+) sum_cpu=(\d+)(.*)')
rows = []; g1b = {}; ggt = {}
for l in open(p, encoding='latin-1'):
    m = g3.match(l)
    if m:
        pl = m.group(5).split(',')
        try: pos = tuple(float(x) for x in pl[:3])
        except ValueError: pos = None
        rows.append((float(m.group(2)), int(m.group(3)), int(m.group(4)), pos)); continue
    m = g1.match(l)
    if m: g1b[int(m.group(1))] = (int(m.group(3)), float(m.group(4)), float(m.group(6))); continue
    m = gt.match(l)
    if m: ggt[int(m.group(1))] = (int(m.group(2)), m.group(3).strip()[:120])
if not rows: sys.exit('no [g3c] rows (ROGUESQ_G3C_LOG=1?)')
bins = collections.defaultdict(list)
for r in rows: bins[int(r[0] // W)].append(r)
slow = slowlim = slowcost = 0
for k in sorted(bins):
    b = bins[k]; dt = max(b[-1][0] - b[0][0], 1e-6)
    tps = (b[-1][1] - b[0][1]) / dt
    lim = collections.Counter(r[2] for r in b)
    path = 0.0
    for a, c in zip(b, b[1:]):
        if a[3] and c[3]:
            d = sum((x - y) ** 2 for x, y in zip(a[3], c[3])) ** .5
            if d < 1e4: path += d
    s0 = int(k * W); sec = [g1b[s] for s in range(s0, s0 + int(W)) if s in g1b]
    sd = sum(x[1] for x in sec) / len(sec) if sec else float('nan')
    gts = [ggt[s] for s in range(s0, s0 + int(W)) if s in ggt]
    tag = ''
    if tps < 45 and len(b) >= 250:
        slow += 1; nl = sum(v for kk, v in lim.items() if kk != 1)
        if nl > len(b) / 2: slowlim += 1; tag = ' SLOW H-limit'
        elif sd == sd and sd > 13.0: slowcost += 1; tag = ' SLOW H-cost'
        else: tag = ' SLOW H-other'
    print(f"t{s0:4d} vi={len(b):4d} tasks/s={tps:5.1f} lim={dict(sorted(lim.items()))} path/s={path/dt:8.1f} sd_wall={sd:5.2f}"
          f" gt={gts[0] if gts else '-'}{tag}")
print(f"SUMMARY windows={len(bins)} slow_windows={slow} H-limit={slowlim} H-cost={slowcost} H-other={slow-slowlim-slowcost}")
