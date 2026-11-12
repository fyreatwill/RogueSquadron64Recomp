#!/usr/bin/env python3
"""s7207: distinct presented images per second (g5b_capture .raw), labelled by the VI origin RT64 presented through in that second
(ROGUESQ_PRESENT_RING Q rows, skip=0). Both use mach seconds (raw displayTime/24e6, ring wall t), so no alignment is needed.
A frame is new if any byte differs from the previous kept frame (thr=0) or mean abs diff > thr.
usage: s7207_distinct_by_vi.py ARM.raw ring_ARM.txt [thr=0]   -> per-second rows + per-VI-origin totals"""
import struct, sys, collections
raw, ring = sys.argv[1], sys.argv[2]; thr = float(sys.argv[3]) if len(sys.argv) > 3 else 0
Q = []
for l in open(ring):
    if l.startswith('Q '):
        p = l.split(); kv = dict(x.split('=', 1) for x in p[2:] if '=' in x)
        Q.append((float(p[1]), kv.get('vi', '?'), kv.get('skip', '0')))
t0 = Q[0][0]
qs = collections.defaultdict(collections.Counter)
for t, vi, sk in Q:
    if sk == '0': qs[int(t - t0)][vi] += 1
f = open(raw, 'rb'); hd = f.read(16); _, w, h = struct.unpack('<QII', hd); f.seek(0); fs = w * h * 3
prev = None; dist = collections.Counter(); deliv = collections.Counter()
import array
while True:
    hd = f.read(16); d = f.read(fs)
    if len(d) < fs: break
    t = struct.unpack('<Q', hd[:8])[0] / 24e6 - t0; s = int(t); deliv[s] += 1
    if prev is None: new = True
    elif thr == 0: new = d != prev
    else:
        a = memoryview(d)[::7]; b = memoryview(prev)[::7]; new = sum(abs(x - y) for x, y in zip(a, b)) / len(a) > thr
    if new: dist[s] += 1; prev = d
byvi = collections.defaultdict(lambda: [0, 0, 0])
print('s  deliv distinct presents  dominant-vi')
for s in sorted(set(dist) | set(deliv)):
    vi = qs[s].most_common(1)[0][0] if qs[s] else '-'
    print(f'{s:3d} {deliv[s]:4d} {dist[s]:4d} {sum(qs[s].values()):4d}  {vi} {dict(qs[s]) if len(qs[s]) > 1 else ""}')
    if 0 < deliv[s] and s > 0: e = byvi[vi]; e[0] += 1; e[1] += dist[s]; e[2] += sum(qs[s].values())
print('per dominant VI: seconds, distinct/s, presents/s')
for vi, (n, dd, pp) in sorted(byvi.items(), key=lambda x: -x[1][0]): print(f'  {vi} {n:3d}s distinct {dd/n:5.1f}/s presents {pp/n:5.1f}/s')
