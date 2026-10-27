#!/usr/bin/env python3
"""G1e: consecutive-VI framebuffer dump difference by lag k.
Usage: g1e_vi_period.py <fbd_dir> [start] [count]. Prints mean abs diff for lag 1..4.
s6451: lvl1 retail lag1~7.6 (constant), lag2~0.45 => dumps alternate between two
field patterns every VI, so md5 run-length is NOT a frame-period measure."""
import glob, sys
d, a, n = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 1500, int(sys.argv[3]) if len(sys.argv) > 3 else 40
L = [open(f, 'rb').read()[-230400:][::7] for f in sorted(glob.glob(d + '/*.ppm'))[a:a + n]]
for k in (1, 2, 3, 4):
    s = [sum(abs(p - q) for p, q in zip(L[i], L[i + k])) / len(L[i]) for i in range(len(L) - k)]
    print('lag', k, 'mean', round(sum(s) / len(s), 2))
