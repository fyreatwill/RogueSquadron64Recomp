#!/usr/bin/env python3
"""s6755: VI-thread edge integrity and game frame cadence from a ROGUESQ_G1E_TL timeline (<file>.<pid>, see g1e_tl.py).
Code 1 = VI edge (arg = total_vis), 3 = update_screen begin, 15 = osViSwapBuffer. Reports per-code wall rates, VI edges
that repeat the previous total_vis (an extra loop pass: extra ScreenUpdate + VI retrace message) or skip one, and the
swap-to-swap interval histogram in VIs (hardware: the game never swaps faster than its retrace wait allows).
usage: g3_vi_edges.py TIMELINE [TIMELINE...]"""
import collections, struct, sys

for path in sys.argv[1:]:
    raw = open(path, "rb").read()
    ev = sorted(struct.unpack_from("<qIIii", raw, i * 24)[:3] for i in range(len(raw) // 24))
    ev = [e for e in ev if e[0]]
    print(f"== {path}")
    for code, name in ((1, "VI edge"), (3, "update_screen"), (15, "osViSwapBuffer")):
        ts = [e[0] for e in ev if e[1] == code]
        if len(ts) > 2:
            print(f"  {name:15s} n={len(ts):6d} rate={(len(ts) - 1) / ((ts[-1] - ts[0]) / 1e6):.3f}/s")
    vi = [e for e in ev if e[1] == 1]
    if len(vi) > 2:
        dup = sum(1 for a, b in zip(vi, vi[1:]) if b[2] == a[2])
        skip = sum(1 for a, b in zip(vi, vi[1:]) if b[2] > a[2] + 1)
        span = (vi[-1][0] - vi[0][0]) / 1e6
        print(f"  total_vis {vi[0][2]}..{vi[-1][2]} = {(vi[-1][2] - vi[0][2]) / span:.3f} VI/s  repeated={dup}  skipped={skip}")
    sw = [e[0] for e in ev if e[1] == 15]
    h = collections.Counter(round((b - a) / 16666.67) for a, b in zip(sw, sw[1:]))
    print("  swap interval (VIs): " + " ".join(f"{k}:{v}" for k, v in sorted(h.items()) if v > 1))
