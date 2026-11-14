#!/usr/bin/env python3
"""s7310: list the swaps of a ROGUESQ_G5B_FRAME capture with mach time, RNG bytes and RAM presence, and name the frozen swap
(the last swap before the largest wall gap; POSE_FREEZE stops submission ~15 s). usage: s7310_cap_swaps.py cap [-v]"""
import sys, struct, subprocess
f = open(sys.argv[1], 'rb'); sw = []  # [swap, mach, rngbytes, ram]
while True:
    h = f.read(4)
    if len(h) < 4: break
    if h == b'SWAP':
        t, s = struct.unpack('<QI', f.read(12)); sw.append([s, t, 0, 0])
    elif h == b'RAM ': f.seek(16 << 20, 1); sw[-1][3] = 1
    elif h == b'RNG ':
        lo, ln = struct.unpack('<II', f.read(8)); f.seek(ln, 1); sw[-1][2] += ln
    else: break
# mach ticks -> s (Apple silicon timebase 125/3 ns per tick)
tb = 125 / 3 * 1e-9
gaps = [((sw[i + 1][1] - sw[i][1]) * tb, sw[i][0]) for i in range(len(sw) - 1)]
g = max(gaps) if gaps else (0, -1)
print('swaps %d..%d n=%d  max gap %.2f s after swap %d' % (sw[0][0], sw[-1][0], len(sw), g[0], g[1]))
if '-v' in sys.argv:
    for r in sw: print(r[0], r[2], r[3])
