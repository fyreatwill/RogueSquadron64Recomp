#!/usr/bin/env python3
"""s7265 G1c: what fraction of WIDEWIN's extra (wide-only) terrain cells would ROGUESQ_DD_WIDEWIN_R=<R> skip?
Reads the [s7233] ph=.. calls=N in=.. skip=.. wide_by_d8=b0,..,b16 lines (8-cell eye-distance bins of wide-only non-empty cells,
per stream call; emitted whenever R>0, both tog phases) and prints, per phase, wide cells/call, the measured skip/call, and the
predicted skipped share for each candidate R (bins wholly beyond R count fully, the straddling bin pro rata).
s7265 use: R=48 (the s7258 auto stack) skips ~95-98% of the wide cells, i.e. the 'stack' is WIDEWIN off + merge.
Usage: s7265_ww_r_predict.py run.log [R ...]   (default R list 48 56 64 72 80 88 96)"""
import sys
if len(sys.argv) < 2: print(__doc__); sys.exit(1)
Rs = [int(x) for x in sys.argv[2:]] or [48, 56, 64, 72, 80, 88, 96]
acc = {}
for l in open(sys.argv[1], errors="replace"):
    if not l.startswith("[s7233] ph=") or "wide_by_d8=" not in l: continue
    ph = l.split()[1]; n = int(l.split("calls=")[1].split()[0])
    h = [float(x) for x in l.split("wide_by_d8=")[1].split(",")[:17]]
    a = acc.setdefault(ph, [0, [0.0] * 17, 0.0])
    a[0] += n; a[2] += float(l.split("skip=")[1].split()[0]) * n
    for k in range(17): a[1][k] += h[k] * n
if not acc: print("no [s7233] histogram lines (R must be >0 for the tally to run)"); sys.exit(2)
for ph, (n, h, sk) in sorted(acc.items()):
    h = [x / n for x in h]; tot = sum(h)
    print(f"{ph} calls={n} wide/call={tot:.0f} measured_skip/call={sk / n:.0f} ({100 * sk / n / max(tot, 1e-9):.0f}%)")
    print("  d8 bins: " + " ".join(f"{x:.0f}" for x in h))
    for R in Rs:
        s = sum(x for k, x in enumerate(h) if 8 * k >= R) + sum(x * ((8 * k + 8 - R) / 8) for k, x in enumerate(h) if 8 * k < R < 8 * k + 8)
        print(f"  R={R:3d}: skip {s:6.0f}/call = {100 * s / max(tot, 1e-9):5.1f}% of wide cells, keeps {tot - s:6.0f}")
