#!/usr/bin/env python3
"""s7834 G3 pitch: compare guest RAM 0x80137DB0..0x801384E0 (player object 0x80137DBC.., camera block 0x80138458..) between a
retail oracle run (rs64_oracle --pc-ram-dump 0x80043918:0x80137DB0:0x801384E0) and a port run (ROGUESQ_S7834_RAMDUMP=1), both
sampled at guest PC 0x80043918. Rows are matched by camera position (cam+0x28 words 9..11 = idx 445..447) inside a z window
(default the first lvl2 straight, z 112..86, where both sides fly level). Per word: median |float diff| and equal fraction at
matched rows. --plant IDX:DELTA adds DELTA to one float word in a copy of the retail rows and scores retail-vs-planted
(positive control: that word, and only it, must come out as differing; retail-vs-itself must give 0 differing words).
Usage: s7834_ramdump_cmp.py RETAIL_LOG PORT_LOG [--z 112:86] [--plant 441:0.002] [--top 40]"""
import re, struct, sys, statistics as st
BASE = 0x80137DB0
f = lambda u: struct.unpack('>f', struct.pack('>I', u))[0]
g = lambda x: struct.unpack('>I', struct.pack('>f', x))[0]

def rows(p):
    r = []
    for ln in open(p, 'rb'):
        if ln.startswith(b'[ramdump]'):
            m = re.search(rb' n=(\d+) w=([0-9A-F]+)', ln)
            h = m.group(2)
            if len(h) == 460 * 8: r.append((int(m.group(1)), [int(h[i:i + 8], 16) for i in range(0, len(h), 8)]))
    return r

def window(X, z0, z1):
    out = []
    for n, w in X:
        x, y, z = (f(w[k]) for k in (445, 446, 447))
        if z1 <= z <= z0 and (x, y, z) != (0, 0, 0):
            out.append((n, w, x, z))
    return out

def score(A, B, top, label):
    pairs = [(a, min(B, key=lambda b: (b[2] - a[2]) ** 2 + (b[3] - a[3]) ** 2)) for a in A]
    nw = len(A[0][1])
    res = []
    for k in range(nw):
        eq = sum(1 for a, b in pairs if a[1][k] == b[1][k])
        d = [abs(f(a[1][k]) - f(b[1][k])) for a, b in pairs]
        d = [x for x in d if x == x]
        med = st.median(d) if d else 0.0
        res.append((k, eq / len(pairs), med, f(pairs[len(pairs) // 2][0][1][k]), f(pairs[len(pairs) // 2][1][1][k])))
    dpos = st.median(((a[2] - b[2]) ** 2 + (a[3] - b[3]) ** 2) ** 0.5 for a, b in pairs)
    diff = [r for r in res if r[1] < 0.5 and r[2] > 1e-6]
    print(f'== {label}: rows {len(A)} vs {len(B)}, median matched xz gap {dpos:.4f}, differing words {len(diff)}')
    for k, eq, med, va, vb in diff[:top]:
        print(f'  idx {k:3d} addr {BASE + 4 * k:08X} eq {eq:.2f} med|d| {med:.6f}  A {va:.6f} B {vb:.6f}')
    return diff

if __name__ == '__main__':
    a = sys.argv[1:]
    z0, z1, top, plant = 112.0, 86.0, 40, None
    if '--z' in a: z0, z1 = map(float, a[a.index('--z') + 1].split(':'))
    if '--top' in a: top = int(a[a.index('--top') + 1])
    if '--plant' in a: i, dv = a[a.index('--plant') + 1].split(':'); plant = (int(i), float(dv))
    R = window(rows(a[0]), z0, z1); P = window(rows(a[1]), z0, z1)
    score(R, R, top, 'control retail vs retail (expect 0 differing)')
    if plant:
        Q = [(n, w[:plant[0]] + [g(f(w[plant[0]]) + plant[1])] + w[plant[0] + 1:], x, z) for n, w, x, z in R]
        d = score(R, Q, top, f'control retail vs planted idx {plant[0]} +{plant[1]} (expect exactly that word)')
        print('  PLANT', 'PASS' if [r[0] for r in d] == [plant[0]] else 'FAIL')
    score(R, P, top, 'retail (A) vs port (B)')
