#!/usr/bin/env python3
"""s6322: fit cell scale s: circular mean of AA94 cells per frame vs (camX/s, camZ/s) mod dim."""
import re, sys, math
log = sys.argv[1]; dim = float(sys.argv[2]) if len(sys.argv) > 2 else 64.0
frames = []; cur = None
for ln in open(log, errors='replace'):
    if ln.startswith('[camlog]'):
        m = re.search(r'ptr=(\w+) cam=([^ ]*) tt', ln)
        if not m: continue
        v = m.group(2).split(',')
        try: x, z = float(v[9]), float(v[11])
        except Exception: cur = None; continue
        cur = {'ptr': m.group(1), 'x': x, 'z': z, 'cells': []}; frames.append(cur)
    elif ln.startswith('[edgefade5]') and cur is not None:
        m = re.search(r'cell=(-?\d+),(-?\d+)', ln)
        if m: cur['cells'].append((int(m.group(1)), int(m.group(2))))
def cmean(vals):
    a = [v * 2 * math.pi / dim for v in vals]
    return (math.atan2(sum(map(math.sin, a)), sum(map(math.cos, a))) * dim / (2 * math.pi)) % dim
def cd(a, b):
    d = abs(a - b) % dim; return min(d, dim - d)
ptr = max(set(f['ptr'] for f in frames), key=lambda p: sum(len(f['cells']) for f in frames if f['ptr'] == p))
use = [f for f in frames if f['ptr'] == ptr and len(f['cells']) >= 6]
print('ptr', ptr, 'frames', len(use), 'dim', dim)
for s in (eval(sys.argv[3]) if len(sys.argv) > 3 else [0.5, 1, 2, 4, 6.4, 8, 12.8, 16, 25.6, 32, 64]):
    for swap in (0, 1):
        r = []
        for f in use:
            cx = cmean([c[swap] for c in f['cells']]); cz = cmean([c[1 - swap] for c in f['cells']])
            r.append(math.hypot(cd(cx, f['x'] / s % dim), cd(cz, f['z'] / s % dim)))
        r.sort(); print(f's={s:<5} swap={swap} median_resid={r[len(r)//2]:.2f} p90={r[int(len(r)*.9)]:.2f}')
