#!/usr/bin/env python3
"""s5680: rank player-record words (from [pdump] lines) by correlation with stick input.
usage: pdump_fields.py run.log   -- floats only; prints top words by |corr| with sx and sy, plus range."""
import re, struct, sys, math
rows = []
for l in open(sys.argv[1], errors='replace'):
    m = re.match(r'\[pdump\] sx=(\S+) sy=(\S+) btn=0x(\w+) :(.*)', l)
    if not m: continue
    ws = [int(w, 16) for w in re.findall(r'\b[0-9a-f]{8}\b', m[4])][:168]
    if len(ws) == 168: rows.append((float(m[1]), float(m[2]), ws))
print("rows", len(rows), "distinct sx", sorted({r[0] for r in rows}), "sy", sorted({r[1] for r in rows}))
def f(u):
    x = struct.unpack('<f', struct.pack('<I', u))[0]
    return x if math.isfinite(x) and abs(x) < 1e7 else None
def corr(a, b):
    n = len(a); ma = sum(a)/n; mb = sum(b)/n
    va = sum((x-ma)**2 for x in a); vb = sum((y-mb)**2 for y in b)
    return 0 if va*vb == 0 else sum((x-ma)*(y-mb) for x, y in zip(a, b))/math.sqrt(va*vb)
def deriv(v): return [v[i+1]-v[i] for i in range(len(v)-1)]
out = []
for w in range(0x2A0//4):
    v = [f(r[2][w]) for r in rows]
    if None in v or max(v) == min(v): continue
    d = deriv(v); sx = [r[0] for r in rows][:-1]; sy = [r[1] for r in rows][:-1]
    out.append((max(abs(corr(d, sx)), abs(corr(d, sy))), w, corr(d, sx), corr(d, sy), min(v), max(v)))
for c, w, cx, cy, lo, hi in sorted(out, reverse=True)[:15]:
    print(f"+0x{w*4:03X} |c|={c:.2f} dcorr_sx={cx:+.2f} dcorr_sy={cy:+.2f} range=[{lo:.2f},{hi:.2f}]")
