#!/usr/bin/env python3
"""Decode N64 Mtx blocks (8 words int halves + 8 words frac halves) from the
s4631 M4 matrix-span capture and compare port vs retail row norms/orthogonality.
Usage: m4_matrix_decode.py <capture_dir>"""
import re, sys, os, math

def dec(w):
    w = [int(x, 16) for x in w]
    h = []; f = []
    for x in w[:8]: h += [(x >> 16) & 0xffff, x & 0xffff]
    for x in w[8:]: f += [(x >> 16) & 0xffff, x & 0xffff]
    s = lambda v: v - 65536 if v >= 32768 else v
    return [[s(h[4 * r + c]) + f[4 * r + c] / 65536 for c in range(4)] for r in range(4)]

def norms(m): return [round(math.sqrt(sum(v * v for v in m[r][:3])), 3) for r in range(3)]
def dots(m):
    d = lambda a, b: sum(x * y for x, y in zip(a, b))
    return [round(d(m[0][:3], m[1][:3]), 2), round(d(m[0][:3], m[2][:3]), 2), round(d(m[1][:3], m[2][:3]), 2)]

d = sys.argv[1]
print("PORT")
seen = set()
for l in open(os.path.join(d, 'port.log'), errors='replace'):
    m = re.match(r'\[m4-mat\] task=(\d+) phase=5 mem=\S+ dram=0x(\w+) w=(\S+)', l)
    if m and m.group(3) not in seen:
        seen.add(m.group(3)); M = dec(m.group(3).split(','))
        print(m.group(2), 'norms', norms(M), 'dots', dots(M), 't', [round(v, 1) for v in M[3]])
print("RETAIL")
seen = set()
for n in range(1, 5):
    for l in open(os.path.join(d, 'oracle_arm%d.log' % n), errors='replace'):
        if 'pk:' in l and 'origin=0x006ab400' in l and 'width=512' in l:
            w = tuple(l.split('pk:')[1].split()[:16])
            if w not in seen:
                seen.add(w); M = dec(w)
                print('arm', n, 'norms', norms(M), 'dots', dots(M), 't', [round(v, 1) for v in M[3]])
