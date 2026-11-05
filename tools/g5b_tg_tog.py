#!/usr/bin/env python3
"""s6896 G5b: bin ROGUESQ_G5B_SHEET sheets by the parity of ROGUESQ_G5B_TG_FIX=tog. Sheets within BAND s of a toggle are set aside.
usage: g5b_tg_tog.py sh_x.txt [...]"""
import re, subprocess, sys
BAND = 0.12; TICK = 125 / 3 / 1e9  # Apple silicon mach timebase, 24 MHz
for p in sys.argv[1:]:
    on = off = band = 0; son = set(); soff = set()
    for l in open(p, errors='replace'):
        m = re.match(r'(\d+) (\d+) op=(\w+) area=(\d+) ', l)
        if not (m and m[3] == '0F' and 'C8112220' in l and int(m[4]) >= 100000): continue
        t = int(m[2]) * TICK; f = t % 1.0
        if f < BAND or f > 1 - BAND: band += 1
        elif int(t) & 1: on += 1; son.add(int(m[1]))
        else: off += 1; soff.add(int(m[1]))
    print(f'{p}: sheets fix-on seconds {on} ({len(son)} swaps), fix-off seconds {off} ({len(soff)} swaps), in band {band}')
