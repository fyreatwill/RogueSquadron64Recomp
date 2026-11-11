#!/usr/bin/env python3
"""s7126 wsheet-escape detector from logs only: a KEPT perspective tri (ROGUESQ_W_KEEPLOG) that shares a screen vertex (+-0.6 px) with a
DROPPED tri (ROGUESQ_W_SHEET_DROPLOG) within --ms (default 3) is a sheet-fan member that escaped the cull (the s7125 w6 swap-7641 band shape).
usage: s7126_apex.py keep.txt drop.txt [--ms 3]"""
import sys, bisect, collections
keep, drop = sys.argv[1], sys.argv[2]; ms = float(sys.argv[sys.argv.index('--ms') + 1]) if '--ms' in sys.argv else 3.0
W = ms * 24e3
D = []
for l in open(drop):
    p = l.split(); t = int(p[0]); v = list(map(float, p[1:7])); D.append((t, [(v[0], v[1]), (v[2], v[3]), (v[4], v[5])], p[7:10]))
D.sort(); dt = [d[0] for d in D]
hits = collections.Counter(); ex = []
nk = 0
for l in open(keep):
    p = l.split()
    if len(p) != 12: continue
    nk += 1; t = int(p[0]); v = list(map(float, p[2:8])); kv = [(v[0], v[1]), (v[2], v[3]), (v[4], v[5])]
    i0, i1 = bisect.bisect_left(dt, t - W), bisect.bisect_right(dt, t + W)
    for d in D[i0:i1]:
        if any(abs(a[0] - b[0]) < 0.6 and abs(a[1] - b[1]) < 0.6 for a in kv for b in d[1]):
            hits[p[1]] += 1
            if len(ex) < 25: ex.append('%d %s span=%s kept v=%s W=%s | drop v=%s W=%s dt=%.2fms' % (t, p[1], p[11], ' '.join(p[2:8]), ' '.join(p[8:11]),
                ' '.join('%.1f %.1f' % q for q in d[1]), ' '.join(d[2]), (t - d[0]) / 24e3))
            break
print('kept lines %d, drops %d, kept tris sharing a vertex with a drop within %.1f ms: %s' % (nk, len(D), ms, dict(hits)))
for e in ex: print(' ', e)
