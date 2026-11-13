#!/usr/bin/env python3
"""s7286 G1c: does a higher draw distance actually stream more terrain? Per log: the dd multiplier, the s6893 tile-pool size,
mean terrain-window cells per stream call ([s7233] ph=.. calls=N in=X, emitted when the WIDEWIN stack R>0), spill-arena
'arena full' lines and crash lines. s7286: L4/L12 16:9 dd6 3536/3522 vs dd8 3542/3510 cells per call while the pool grows
6480 -> 11520 entries, i.e. the window (64 deep x 128 wide area cap) binds from dd6 and dd8 only adds pool and cost.
NOTE s7291: in= counts only the retail-equivalent 64x64 window, so this "cells/call" is ~constant by construction; use
tools/s7291_wide_cells.py for the real total.
Usage: s7286_dd_window_cells.py log [log ...]"""
import re, sys
if len(sys.argv) < 2: print(__doc__); sys.exit(1)
for p in sys.argv[1:]:
    dd = pool = "?"; s = n = 0.0; full = crash = 0
    for l in open(p, errors="replace"):
        if l.startswith("[dd] ROGUESQ_DRAW_DISTANCE multiplier"): dd = l.split()[-1]
        elif l.startswith("[s6893] tile pool entries"): pool = l.split("->")[1].split()[0]
        elif l.startswith("[s7233] ph=") and " in=" in l:
            c = int(l.split("calls=")[1].split()[0]); s += float(l.split(" in=")[1].split()[0]) * c; n += c
        elif "arena full" in l: full += 1
        elif re.search(r"CRASH|SIGBUS|SIGSEGV|abort\(", l): crash += 1
    cells = f"{s / n:.0f}" if n else "n/a (no [s7233] lines: WIDEWIN stack off?)"
    print(f"{p}: dd={dd} pool={pool} cells/call={cells} calls={n:.0f} arena_full={full} crash_lines={crash}")
