#!/usr/bin/env python3
"""s7114: same-run on/off split of eye-cell near-plane losses by the odd-mach-second toggle clock (mach/24e6 & 1 = on).

usage: s7114_parity.py tris.bin losscan.txt push.txt [shift_s ...]
Loss = s7107_losscan line whose first reference cell is the eye cell 'c+0+0' and whose dropped min z < 0x100 (the s7108 near-z
criterion, same rule as tools/s7113_raymiss.py), t >= 0. Denominator = swaps inside the flight emit window (first..last 'ce' line).
Episodes = losses merged when < 0.5 s apart (one wall hug = one episode). shift_s: control splits with the clock shifted by that many
seconds (0.5 s shifts put each half-second of on and off into both bins: a real effect must collapse there)."""
import sys, re, mmap, struct, collections, math
trisb, lsc, pushf = sys.argv[1:4]; SH = [float(x) for x in sys.argv[4:]]
F = open(trisb, 'rb'); d = mmap.mmap(F.fileno(), 0, access=mmap.ACCESS_READ)
M = b'\xf5\xf5\xf5\xf5'; SWM = {}; p = d.find(M)
while p >= 0:
    n = d.find(M, p + 16)
    while n > 0 and (n - p - 16) % 32: n = d.find(M, n + 1)
    t, q = struct.unpack_from('<QI', d, p + 4); SWM[q] = t; p = n
ce = [int(l.split(' m=')[1].split()[0]) for l in open(pushf, errors='replace') if l.startswith('ce ')]
lo, hi = min(ce), max(ce)
rl = re.compile(r'sw\s+(\d+) t=\s*([-\d.]+) lost\s+(\d+) ref (\[.*?\]) -> .*near tris/minz ref (\d+)/([0-9A-F]+) drop (\d+)/([0-9A-F]+)')
loss = []
for line in open(lsc):
    g = rl.search(line)
    if not g or float(g.group(2)) < 0: continue
    if "'c+0+0'" in g.group(4).split(',')[0] and int(g.group(8), 16) < 0x100: loss.append(int(g.group(1)))
fl = [s for s, m in SWM.items() if lo <= m <= hi]
def split(shift):
    par = lambda m: int((m / 24e6) + shift) & 1
    N = collections.Counter(par(SWM[s]) for s in fl)
    L = collections.Counter(par(SWM[s]) for s in loss if s in SWM and lo <= SWM[s] <= hi)
    ep = collections.Counter(); last = None
    for s in sorted(x for x in loss if x in SWM and lo <= SWM[x] <= hi):
        m = SWM[s]
        if last is None or m - last > 0.5 * 24e6: ep[par(m)] += 1
        last = m
    r = lambda k: L[k] / max(N[k], 1) * 1000
    # two-sided binomial-ish z for losses on vs off given swap shares
    n = L[0] + L[1]; pon = N[1] / max(N[0] + N[1], 1); z = (L[1] - n * pon) / math.sqrt(max(n * pon * (1 - pon), 1e-9))
    return f'shift {shift:+.2f} s: swaps off/on {N[0]}/{N[1]}  losses off/on {L[0]}/{L[1]} ({r(0):.2f}/{r(1):.2f} per 1000 swaps)  episodes off/on {ep[0]}/{ep[1]}  z {z:+.2f}'
print(f'flight swaps {len(fl)}, eye-cell near-z losses {len(loss)} (in window {sum(1 for s in loss if s in SWM and lo <= SWM[s] <= hi)})')
print(split(0.0))
for s in SH: print(split(s))
