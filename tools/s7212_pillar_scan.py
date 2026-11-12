#!/usr/bin/env python3
"""s7212: scan a g5b_capture window raw for one-off pillarboxed frames (dark side bands, lit centre, full-width neighbours).
usage: s7212_pillar_scan.py <raw> [x0 x1]   x0/x1 = pillar edges in raw px (default 166 1192 = RT64 vp of a 4:3 box in 1360 wide).
Per frame: mean luma of the two side bands (cols <x0-6 and >x1+6) and the centre; flags frames whose sides are < 1/4 of the centre
and < 8, while the median of the 4 neighbours' sides is >= 12. Positive control: the same test run on a synthetic copy of the
brightest full-width frame with its side bands zeroed (must flag) and on the original (must not)."""
import sys, struct, os
raw = sys.argv[1]; x0, x1 = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (166, 1192)
f = open(raw, 'rb'); t0, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3; n = os.path.getsize(raw) // rec
Y0 = 34  # skip the title bar rows
def frame(i):
    f.seek(i * rec); t = struct.unpack('<Q', f.read(8))[0]; f.seek(i * rec + 16)
    return t, bytearray(f.read(w * h * 3))
def bands(a):
    # luma ~ (r+2g+b)/4 on every 4th column of every 8th row (C-speed sums over byte slices)
    sl, ns, cl, nc = 0, 0, 0, 0
    for y in range(Y0, h, 8):
        row = a[y * w * 3:(y + 1) * w * 3]
        for lo, hi, side in ((0, x0 - 6, 1), (x1 + 6, w, 1), (x0 + 40, x1 - 40, 0)):
            seg = row[lo * 3:hi * 3]; v = sum(seg[0::12]) + 2 * sum(seg[1::12]) + sum(seg[2::12]); k = len(seg[0::12])
            if side: sl += v; ns += 4 * k
            else: cl += v; nc += 4 * k
    return sl / ns, cl / nc
def zero_sides(a):
    a = bytearray(a)
    for y in range(h):
        o = y * w * 3; a[o:o + x0 * 3] = bytes(x0 * 3); a[o + x1 * 3:o + w * 3] = bytes((w - x1) * 3)
    return a
def boxed(s, c, nb): return s < 8 and s < c / 4 and nb >= 12
T, S, C = [], [], []
for i in range(n):
    t, a = frame(i); s, c = bands(a); T.append(t); S.append(s); C.append(c)
hits = []
for i in range(n):
    nb = sorted(S[j] for j in (i - 2, i - 1, i + 1, i + 2) if 0 <= j < n)
    nbm = nb[len(nb) // 2] if nb else 0
    if boxed(S[i], C[i], nbm): hits.append((i, T[i], S[i], C[i], nbm))
print('frames', n, 'span %.2f s' % ((T[-1] - T[0]) / 24e6), 'mach %d..%d' % (T[0], T[-1]))
dark = sum(1 for s, c in zip(S, C) if s < 8 and c < 8); full = sum(1 for s in S if s >= 12)
print('all-dark frames', dark, 'full-width lit frames', full)
for h_ in hits: print('HIT frame %d mach %d side %.1f centre %.1f neighbours %.1f' % h_)
print('hits', len(hits))
# positive control
b = max(range(n), key=lambda i: min(S[i], C[i])); _, a = frame(b); s0, c0 = bands(a); a2 = zero_sides(a)
s1, c1 = bands(a2)
ok = boxed(s1, c1, s0) and not boxed(s0, c0, s0)
print('control frame %d: orig side %.1f centre %.1f -> %s; boxed side %.1f centre %.1f -> %s; CONTROL %s' % (b, s0, c0, boxed(s0, c0, s0), s1, c1, boxed(s1, c1, s0), 'PASS' if ok else 'FAIL'))
if len(sys.argv) > 4:  # dump luma series around a mach time: s7212_pillar_scan.py raw x0 x1 <mach>
    m = int(sys.argv[4]); k = min(range(n), key=lambda i: abs(T[i] - m))
    for i in range(max(0, k - 12), min(n, k + 13)): print('  f%d %+.1f ms side %.1f centre %.1f' % (i, (T[i] - m) / 24e3, S[i], C[i]))
