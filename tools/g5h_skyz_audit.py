#!/usr/bin/env python3
"""s6946 G5h: summarise a ROGUESQ_DD_SKYZ_AUD file (DD_SKYZ=tog run). Rows: swap mach parity sky_ring oth_ring sky_other oth_other [sky_rw oth_rw] (s6946: draws under an actually rewritten depth).
oth_ring > 0 means a depth SKYZ rewrites (on odd seconds) is consumed by a non-sky mode: H-leak. oth_other > 0 is the control (non-sky prim-z draws are seen).
Prints totals per parity, per 60 s bin, and the leaking mode words. s6947: a 10th column is the SEL rule state (ROGUESQ_DD_SKYZ_SEL=tog), totals split by it.   g5h_skyz_audit.py AUD"""
import sys
rows = []; leaks = []
for l in open(sys.argv[1]):
    if l.startswith('#'): leaks.append(l.strip()); continue
    p = l.split()
    if len(p) == 21: rows.append([int(x) for x in p]); continue
    if len(p) in (7, 9, 10): rows.append([int(x) for x in p[:9]] + [0, 0] * (len(p) == 7) + [int(p[9]) if len(p) == 10 else -1])
if not rows: sys.exit('no rows')
WHY = ['put', 'late', 'selMode', 'selDrawNoPz', 'selDrawPz', 'selEnd', 'offlive', 'noring', 'lateMiss']
if len(rows[0]) == 21:  # s6948: rows carry SEL2 state, un-rewritten sky draws by reason (cols 11-19) and rewritten non-sky draws (col 20)
    T3 = {}
    for r in rows:
        k = (r[2], 'val' if not r[9] else 'sel2' if r[10] else 'sel'); t = T3.setdefault(k, [0] * 13); t[12] += 1
        t[0] += r[3]; t[1] += r[7]; t[2] += r[8]
        for i in range(9): t[3 + i] += r[11 + i]
    print('s6948 parity rule swaps sky_ring sky_rw oth_rw | unrewritten sky draws by reason:', *WHY)
    for k in sorted(T3): t = T3[k]; print('on ' if k[0] else 'off', k[1], t[12], t[0], t[1], t[2], '|', *t[3:12], f' miss%={100 * (1 - t[1] / t[0]) if t[0] else 0:.2f}')
    rows = [r[:10] for r in rows]
t0 = rows[0][1]; tot = {0: [0] * 6, 1: [0] * 6}; B = {}
for r in rows:
    for i in range(6): tot[r[2]][i] += r[3 + i]
    b = B.setdefault(int((r[1] - t0) / 24e6 // 60), [0] * 5)
    for i in range(4): b[i] += r[3 + i]
    b[4] += 1
print('parity sky_ring oth_ring(would-leak) sky_other oth_other(control) sky_rw oth_rw(leak)')
for k in (0, 1): print('on ' if k else 'off', *tot[k])
if any(r[9] >= 0 for r in rows):
    T2 = {}
    for r in rows:
        t = T2.setdefault((r[2], r[9]), [0] * 7); t[6] += 1
        for i in range(6): t[i] += r[3 + i]
    print('parity sel swaps sky_ring oth_ring sky_other oth_other sky_rw oth_rw')
    for k in sorted(T2): print('on ' if k[0] else 'off', 'sel' if k[1] else 'val', T2[k][6], *T2[k][:6])
print('bin(60s) swaps sky_ring oth_ring sky_other oth_other')
for k in sorted(B): print(f'{k * 60:5d} {B[k][4]:6d}', *B[k][:4])
print(len(leaks), 'leaking modes'); [print(x) for x in leaks]
