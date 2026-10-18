#!/usr/bin/env python3
"""s5465: usage rdram_flags_at.py <rd_dir> lo hi — per consecutive dump pair, first pair where the overlay window
0xA5140..0xA5E00 changes (overlay swap), then small-value (<=0xFF -> <=0xFF) word flips in [0,0xA0000) in the pairs
around it."""
import sys, glob, re, os
from array import array
d, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
fs = {}
for f in glob.glob(os.path.join(d, 'rdram_*.bin')):
    fs[int(re.search(r'rdram_(\d+)_', f).group(1))] = f
ns = sorted(n for n in fs if lo <= n <= hi)
def ld(n):
    x = array('I'); x.frombytes(open(fs[n], 'rb').read(0xA6000)); return x
prev = None; pn = None; hit = None
for n in ns:
    cur = ld(n)
    if prev is not None:
        ov = sum(1 for i in range(0xA5140 // 4, 0xA5E00 // 4) if cur[i] != prev[i])
        lowch = sum(1 for i in range(0xA0000 // 4) if cur[i] != prev[i])
        print('%d->%d overlay-words-changed=%d low-words-changed=%d' % (pn, n, ov, lowch))
        if ov > 200 and hit is None:
            hit = (pn, n)
            for i in range(0xA0000 // 4):
                a, b = prev[i], cur[i]
                if a != b and a <= 0xFF and b <= 0xFF:
                    print('  FLIP %06X: %02X -> %02X' % (i * 4, a, b))
    prev, pn = cur, n
