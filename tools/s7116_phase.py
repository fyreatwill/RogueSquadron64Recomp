#!/usr/bin/env python3
"""s7116: pooled phase histogram of eye-cell near-z losses vs the tog1 toggle clock (mach/24e6 mod 2; [0,1) off, [1,2) on).
usage: s7116_phase.py tris.bin losscan.txt push.txt [tris2 losscan2 push2 ...]
Reuses the tools/s7114_parity.py loss rule. Prints per-0.25 s phase bin: swaps, losses, episode starts (episode = losses < 0.5 s apart),
and the pooled off/on totals with a binomial z. Why: the +-0.5 s shift controls of s7114_parity do not collapse when losses cluster
inside episodes and the lift's effect has a phase lag (off-early after an on second), so the phase table is the readable control."""
import sys, re, mmap, struct, collections, math
rl = re.compile(r'sw\s+(\d+) t=\s*([-\d.]+) lost\s+(\d+) ref (\[.*?\]) -> .*near tris/minz ref (\d+)/([0-9A-F]+) drop (\d+)/([0-9A-F]+)')
NB = 8; SW = [0] * NB; LS = [0] * NB; EP = [0] * NB; runs = []
a = sys.argv[1:]
for i in range(0, len(a), 3):
    trisb, lsc, pushf = a[i:i + 3]
    F = open(trisb, 'rb'); d = mmap.mmap(F.fileno(), 0, access=mmap.ACCESS_READ)
    M = b'\xf5\xf5\xf5\xf5'; SWM = {}; p = d.find(M)
    while p >= 0:
        n = d.find(M, p + 16)
        while n > 0 and (n - p - 16) % 32: n = d.find(M, n + 1)
        t, q = struct.unpack_from('<QI', d, p + 4); SWM[q] = t; p = n
    ce = [int(l.split(' m=')[1].split()[0]) for l in open(pushf, errors='replace') if l.startswith('ce ')]
    lo, hi = min(ce), max(ce)
    loss = []
    for line in open(lsc):
        g = rl.search(line)
        if not g or float(g.group(2)) < 0: continue
        if "'c+0+0'" in g.group(4).split(',')[0] and int(g.group(8), 16) < 0x100: loss.append(int(g.group(1)))
    b = lambda m: int(((m / 24e6) % 2.0) * NB / 2.0) % NB
    for s, m in SWM.items():
        if lo <= m <= hi: SW[b(m)] += 1
    last = None; rl_ = [0, 0]; re_ = [0, 0]
    for s in sorted(x for x in loss if x in SWM and lo <= SWM[x] <= hi):
        m = SWM[s]; k = b(m); LS[k] += 1; rl_[k >= NB // 2] += 1
        if last is None or m - last > 0.5 * 24e6: EP[k] += 1; re_[k >= NB // 2] += 1
        last = m
    runs.append((trisb, rl_, re_))
for r in runs: print(f'{r[0]}: losses off/on {r[1][0]}/{r[1][1]}  episodes off/on {r[2][0]}/{r[2][1]}')
print('phase(s)  state  swaps  losses  episodes')
for k in range(NB): print(f'{k * 2 / NB:4.2f}-{(k + 1) * 2 / NB:4.2f}  {"on " if k >= NB // 2 else "off"}  {SW[k]:6d}  {LS[k]:6d}  {EP[k]:6d}')
def z(X):
    o, n_ = sum(X[:NB // 2]), sum(X[NB // 2:]); n = o + n_; pon = sum(SW[NB // 2:]) / max(sum(SW), 1)
    return o, n_, (n_ - n * pon) / math.sqrt(max(n * pon * (1 - pon), 1e-9))
print('pooled losses off/on %d/%d z %+.2f' % z(LS)); print('pooled episodes off/on %d/%d z %+.2f' % z(EP))
