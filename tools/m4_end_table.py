#!/usr/bin/env python3
"""Tabulate [m4-end] port task-end accumulator lines by (phase, kind). s5005."""
import re, sys, collections
rows = collections.defaultdict(lambda: [0, 0, 0])
for line in open(sys.argv[1], errors="replace"):
    m = re.match(r"\[m4-end\] task=(\d+) phase=(\d+) kind=(\d) sat8000=(\d+) nz=(\d+)", line)
    if not m:
        continue
    _, ph, kind, sat, nz = map(int, m.groups())
    r = rows[(ph, kind)]
    r[0] += 1
    r[1] += sat > 0
    r[2] += nz > 0
print("phase kind tasks sat8000>0 nz>0")
for (ph, kind), (n, s, z) in sorted(rows.items()):
    print(ph, kind, n, s, z)
