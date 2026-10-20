#!/usr/bin/env python3
# s5682: correlate per-poll ship pos deltas with record vel from [pd2] log rows.
import re, sys
import numpy as np
rows = []
for l in open(sys.argv[1], errors="replace"):
    m = re.search(r"\[pd2\].*pos=([-\d.e]+),([-\d.e]+),([-\d.e]+) vel=([-\d.e]+),([-\d.e]+),([-\d.e]+)", l)
    if m: rows.append([float(x) for x in m.groups()])
a = np.array(rows); print("rows", len(a))
if len(a) > 10:
    d = np.diff(a[:, :3], axis=0); v = a[1:, 3:]
    for i in range(3):
        for j in range(3):
            c = np.corrcoef(d[:, i], v[:, j])[0, 1] if d[:, i].std() > 0 and v[:, j].std() > 0 else float("nan")
            print(f"dpos{'xyz'[i]} vs vel{'xyz'[j]}: {c:.3f}")
