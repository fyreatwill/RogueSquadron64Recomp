#!/usr/bin/env python3
"""s7537: score SP_LATE cost pairs from the present ring alone (the quiet harness logs no [g1b]).
usage: s7537_ring_cost.py <dir> <arm>... [--from S] [--to S]
Per arm over ring seconds [from, to): gen/s (new game frames), shown/s (Q lines with wl=1), slow_s (seconds with gen < 57),
wl_ms p50/p90 over frames with work (flight 7-10 ms, menus ~1 ms: a window spent in a menu shows as low p50),
max gap between consecutive new frames (ms). shown/s = presents with new render work (wl counter advanced). Pairs <x>e/<x>l print the late-minus-early gen/s delta and a H-free/H-cost verdict
(H-cost if late gen/s < 59 while early >= 59, or late < early - 0.5)."""
import sys, re, statistics as st
a = [x for x in sys.argv[1:] if not x.startswith('--')]
fr = float(sys.argv[sys.argv.index('--from') + 1]) if '--from' in sys.argv else 60.0
to = float(sys.argv[sys.argv.index('--to') + 1]) if '--to' in sys.argv else 1e9
d, arms = a[0], [x for x in a[1:] if not re.match(r'^[\d.]+$', x)]
Q = re.compile(r'^Q ([\d.]+) id=\d+ wl=(\d+) .*? gen=(\d+) wl_ms=([\d.]+)')
res = {}
print('arm      gen/s shown/s slow_s wl50 wl90 maxgap_ms frames')
for arm in arms:
    rows = []
    for l in open('%s/ring_%s.txt' % (d, arm), errors='replace'):
        m = Q.match(l)
        if m: rows.append((float(m[1]), int(m[2]), int(m[3]), float(m[4])))
    rows = [(t, int(i == 0 or w != rows[i - 1][1]), g, ms) for i, (t, w, g, ms) in enumerate(rows)]  # wl is cumulative: 1 = this present rendered new work
    if not rows: print('%-8s no ring rows' % arm); continue
    t0 = rows[0][0]; w = [r for r in rows if fr <= r[0] - t0 < to]
    if not w: print('%-8s empty window' % arm); continue
    span = w[-1][0] - w[0][0]; gens = [r for i, r in enumerate(w) if i and r[2] != w[i - 1][2]]
    persec = {}
    for r in gens: persec[int(r[0] - t0)] = persec.get(int(r[0] - t0), 0) + 1
    full = [s for s in persec if fr + 1 <= s < int(w[-1][0] - t0)]
    slow = sum(1 for s in range(int(fr) + 1, int(w[-1][0] - t0)) if persec.get(s, 0) < 57)
    wl = sorted(r[3] for r in w if r[1] and r[3] > 0)
    gap = max((gens[i][0] - gens[i - 1][0]) * 1e3 for i in range(1, len(gens))) if len(gens) > 1 else 0
    g = len(gens) / span if span else 0; sh = sum(1 for r in w if r[1]) / span if span else 0
    res[arm] = g
    print('%-8s %5.1f %7.1f %6d %4.1f %4.1f %9.1f %6d' % (arm, g, sh, slow, wl[len(wl) // 2] if wl else 0, wl[int(len(wl) * .9)] if wl else 0, gap, len(gens)))
bad = 0
for arm in arms:
    if arm.endswith('e') and arm[:-1] + 'l' in res and arm in res:
        e, l = res[arm], res[arm[:-1] + 'l']; c = (l < 59 <= e) or l < e - 0.5; bad += c
        print('pair %-6s early %.1f late %.1f delta %+.2f -> %s' % (arm[:-1], e, l, l - e, 'H-cost' if c else 'H-free'))
sys.exit(1 if bad else 0)
