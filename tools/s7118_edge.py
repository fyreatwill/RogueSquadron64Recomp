#!/usr/bin/env python3
"""s7118: edge-excluded rate comparison of eye-cell near-z losses for a 1 s toggle (mach/24e6 mod 2; [0,1) = A, [1,2) = B).
usage: s7118_edge.py [W=0.1] tris.bin losscan.txt push.txt [tris2 losscan2 push2 ...]
Same loss rule and swap clock as tools/s7116_phase.py. Swaps (and losses) within W s after either toggle edge are set aside, because a
presented frame is built from an earlier tick (s7117: k-1 join, ~3 ms swap lag, plus queue depth), so the first frames after an edge
still show the previous state. Prints per run and pooled: steady A/B losses, swaps, rate ratio, binomial z, and the edge-window counts
per edge direction (A->B at phase 1.0, B->A at phase 0.0). Pre-registered in s7118 with W = 0.1 s before runs k, l were analysed."""
import sys, re, mmap, struct, math
rl = re.compile(r'sw\s+(\d+) t=\s*([-\d.]+) lost\s+(\d+) ref (\[.*?\]) -> .*near tris/minz ref (\d+)/([0-9A-F]+) drop (\d+)/([0-9A-F]+)')
a = sys.argv[1:]; W = 0.1
if len(a) % 3 == 1: W = float(a[0]); a = a[1:]
P = {'sw': [0, 0], 'ls': [0, 0], 'edge_sw': [0, 0], 'edge_ls': [0, 0]}
def zr(ls, sw):
    n = ls[0] + ls[1]; pb = sw[1] / max(sw[0] + sw[1], 1)
    return (ls[1] - n * pb) / math.sqrt(max(n * pb * (1 - pb), 1e-9))
def rep(tag, R):
    ra = R['ls'][0] / max(R['sw'][0], 1) * 1e4; rb = R['ls'][1] / max(R['sw'][1], 1) * 1e4
    print(f"{tag}: steady A/B losses {R['ls'][0]}/{R['ls'][1]} swaps {R['sw'][0]}/{R['sw'][1]} per 1e4 {ra:.2f}/{rb:.2f}"
          f" ratio B/A {rb / ra if ra else float('nan'):.2f} z {zr(R['ls'], R['sw']):+.2f} | edge(<{W}s) B->A losses {R['edge_ls'][0]}"
          f" of {R['edge_sw'][0]} swaps, A->B {R['edge_ls'][1]} of {R['edge_sw'][1]}")
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
    loss = set()
    for line in open(lsc):
        g = rl.search(line)
        if not g or float(g.group(2)) < 0: continue
        if "'c+0+0'" in g.group(4).split(',')[0] and int(g.group(8), 16) < 0x100: loss.add(int(g.group(1)))
    R = {'sw': [0, 0], 'ls': [0, 0], 'edge_sw': [0, 0], 'edge_ls': [0, 0]}
    for s, m in SWM.items():
        if not lo <= m <= hi: continue
        ph = (m / 24e6) % 2.0; st = int(ph >= 1.0); key = 'edge_' if (ph % 1.0) < W else ''
        R[key + 'sw'][st] += 1
        if s in loss: R[key + 'ls'][st] += 1
    rep(trisb, R)
    for k in P: P[k] = [P[k][0] + R[k][0], P[k][1] + R[k][1]]
rep('POOLED', P)
