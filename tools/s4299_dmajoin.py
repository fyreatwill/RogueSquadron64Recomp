#!/usr/bin/env python3
"""s4299: list [dma] rows whose RAM span overlaps [lo,hi) (phys) in a run log; also first/last [dma] line numbers."""
import re, sys
log, lo, hi = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
n = 0
for i, l in enumerate(open(log, errors="replace")):
    m = re.match(r"\[dma\] rom_off=0x(\w+) -> ram=0x(\w+) size=0x(\w+)", l)
    if not m: continue
    n += 1
    rom, ram, sz = (int(x, 16) for x in m.groups())
    p = ram & 0x1FFFFFFF
    if p < hi and p + sz > lo:
        print(i, l.strip())
print("total dma rows", n)
