#!/usr/bin/env python3
"""s7291 G1c: the real wide-window cell count per stream call. [s7233] in= counts ONLY non-empty cells inside the retail-equivalent
min(w,64) x min(d,64) window (rs64_s7233_cell increments s7233_in before any distance test), so it is ~constant by construction and
cannot show a deeper/wider window (s7286-s7290 read it as "cells/call" and concluded the window binds). The wide-only cells are the
wide_by_d8 histogram (8-cell eye-distance bins, bin 16 = >=128) and skip= is how many of them WIDEWIN_R dropped (centre > R).
Prints per log: calls, retail in, wide total, skipped, emitted wide (= total - skip), emitted total, and the wide histogram mass beyond R.
Only ph=1 lines with calls>0 and a non-zero histogram (in flight) are pooled. Usage: s7291_wide_cells.py log [log ...]"""
import sys
if len(sys.argv) < 2: print(__doc__); sys.exit(1)
for p in sys.argv[1:]:
    n = sin = swide = sskip = 0.0; r = "?"; h = [0.0] * 17
    for l in open(p, errors="replace"):
        if not l.startswith("[s7233] ph=1 ") or " in=" not in l: continue
        c = int(l.split("calls=")[1].split()[0]); hb = [float(x) for x in l.split("wide_by_d8=")[1].split(",")]
        if c == 0 or sum(hb) == 0: continue
        r = l.split(" r=")[1].split()[0]
        n += c; sin += float(l.split(" in=")[1].split()[0]) * c; sskip += float(l.split(" skip=")[1].split()[0]) * c
        swide += sum(hb) * c; h = [a + b * c for a, b in zip(h, hb)]
    if not n: print(f"{p}: no in-flight [s7233] ph=1 lines"); continue
    w, k, i = swide / n, sskip / n, sin / n
    print(f"{p.split('/')[-1]}: r={r} calls={n:.0f} retail_in={i:.0f} wide={w:.0f} skip={k:.0f} wide_emit={w - k:.0f} "
          f"total_emit={i + w - k:.0f} | far bins d8 11-16: " + ",".join(f"{x / n:.0f}" for x in h[11:]))
