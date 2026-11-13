#!/usr/bin/env python3
"""s7257: list seconds with <55 gfx tasks per [g1b] log, grouped into runs (gap<=2 s).
Usage: s7257_dip_runs.py LOG... ; prints per log: total <55 s, runs (t0,t1,min tasks), and the count outside the
route-transition seconds common to every arm (5,11,28,43-44,59,67 in L4 owner route, s7251/s7250)."""
import re, sys
R = re.compile(r'^\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+)')
COMMON = {5, 11, 28, 43, 44, 59, 67}
for f in sys.argv[1:]:
    bad = []
    for l in open(f, errors='ignore'):
        m = R.match(l)
        if m and int(m[1]) >= 1 and int(m[3]) < 55:
            bad.append((int(m[1]), int(m[3])))
    runs = []
    for t, n in bad:
        if runs and t - runs[-1][1] <= 2:
            runs[-1][1] = t; runs[-1][2] = min(runs[-1][2], n)
        else:
            runs.append([t, t, n])
    extra = [t for t, _ in bad if t not in COMMON]
    print(f"{f.split('/')[-1]}: <55/s {len(bad)} s, beyond-route {len(extra)} s, runs {[tuple(r) for r in runs][:16]}")
