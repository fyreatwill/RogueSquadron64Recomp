#!/usr/bin/env python3
"""s6894 G5b: bin g5b_drops events by the parity of their mach second for ROGUESQ_G5B_KILLSHEET=tog (odd = kill on).
Events within 120 ms of a parity boundary are set aside, since submit and display can straddle it.
usage: g5b_parity.py <events.csv> [minT=0.04] [skip_s=0]"""
import sys
mt = float(sys.argv[2]) if len(sys.argv) > 2 else 0.04; sk = float(sys.argv[3]) if len(sys.argv) > 3 else 0
c = {'odd_kill': 0, 'even_live': 0, 'edge': 0}; rows = []
for l in list(open(sys.argv[1]))[1:]:
    e = l.strip().split(',')
    if float(e[4]) < mt or float(e[1]) < sk: continue
    m = int(e[6]) / 24e6; f = m % 1
    k = 'edge' if (f < 0.12 or f > 0.88) else ('odd_kill' if int(m) & 1 else 'even_live')
    c[k] += 1; rows.append((e[1], e[3], e[4], e[5], k))
print(c); [print(*r) for r in rows]
