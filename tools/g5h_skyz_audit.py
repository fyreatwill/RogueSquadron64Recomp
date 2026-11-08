#!/usr/bin/env python3
"""s6946 G5h: summarise a ROGUESQ_DD_SKYZ_AUD file (DD_SKYZ=tog run). Rows: swap mach parity sky_ring oth_ring sky_other oth_other [sky_rw oth_rw] (s6946: draws under an actually rewritten depth).
oth_ring > 0 means a depth SKYZ rewrites (on odd seconds) is consumed by a non-sky mode: H-leak. oth_other > 0 is the control (non-sky prim-z draws are seen).
Prints totals per parity, per 60 s bin, and the leaking mode words.   g5h_skyz_audit.py AUD"""
import sys
rows = []; leaks = []
for l in open(sys.argv[1]):
    if l.startswith('#'): leaks.append(l.strip()); continue
    p = l.split()
    if len(p) in (7, 9): rows.append([int(x) for x in p] + [0, 0] * (len(p) == 7))
if not rows: sys.exit('no rows')
t0 = rows[0][1]; tot = {0: [0] * 6, 1: [0] * 6}; B = {}
for r in rows:
    for i in range(6): tot[r[2]][i] += r[3 + i]
    b = B.setdefault(int((r[1] - t0) / 24e6 // 60), [0] * 5)
    for i in range(4): b[i] += r[3 + i]
    b[4] += 1
print('parity sky_ring oth_ring(would-leak) sky_other oth_other(control) sky_rw oth_rw(leak)')
for k in (0, 1): print('on ' if k else 'off', *tot[k])
print('bin(60s) swaps sky_ring oth_ring sky_other oth_other')
for k in sorted(B): print(f'{k * 60:5d} {B[k][4]:6d}', *B[k][:4])
print(len(leaks), 'leaking modes'); [print(x) for x in leaks]
