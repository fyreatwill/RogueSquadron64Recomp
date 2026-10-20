#!/usr/bin/env python3
"""s5681: for each [pptr] (off,tgt) series, find float vec3s whose per-sample delta correlates with stick, or with another series' velocity.
usage: pptr_fields.py run.log"""
import re, struct, sys, math, collections
S = collections.defaultdict(list)
for l in open(sys.argv[1], errors='replace'):
    m = re.match(r'\[pptr\] off=(\w+) tgt=(\w+) sx=(\S+) sy=(\S+) :(.*)', l)
    if not m: continue
    ws = [int(w, 16) for w in re.findall(r'\b[0-9a-f]{8}\b', m[5])]
    if len(ws) == 64: S[(m[1], m[2])].append((float(m[3]), float(m[4]), ws))
def f(u):
    x = struct.unpack('<f', struct.pack('<I', u))[0]
    return x if math.isfinite(x) and abs(x) < 1e7 else None
def corr(a, b):
    n = len(a); ma = sum(a)/n; mb = sum(b)/n
    va = sum((x-ma)**2 for x in a); vb = sum((y-mb)**2 for y in b)
    return 0 if va*vb == 0 else sum((x-ma)*(y-mb) for x, y in zip(a, b))/math.sqrt(va*vb)
for k, rows in S.items():
    if len(rows) < 8: continue
    best = []
    for w in range(64):
        v = [f(r[2][w]) for r in rows]
        if None in v or max(v) == min(v): continue
        d = [v[i+1]-v[i] for i in range(len(v)-1)]
        c = max(abs(corr(d, [r[0] for r in rows][:-1])), abs(corr(d, [r[1] for r in rows][:-1])))
        best.append((c, w, min(v), max(v)))
    best.sort(reverse=True)
    print(k, "rows", len(rows), " ".join(f"+{w*4:02X}:c={c:.2f}[{lo:.0f},{hi:.0f}]" for c, w, lo, hi in best[:4]))
