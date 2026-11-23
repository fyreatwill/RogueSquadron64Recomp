#!/usr/bin/env python3
"""s7851: per-mission-tick lifecycle compare of 3D-sound node 0x80137FC4 (+0x08 flags word, +0x40 fade timer), retail vs port.
usage: s7851_snd_node_cmp.py RETAIL_ORACLE_LOG PORT_RAND_TRACE [--control]
Retail: rs64_oracle --hit-cap 100000 --hit-vi-window 0:20000 --watch-pc 0x800FA730 --watch-write 0x137FCC:0x137FD0
  --watch-write 0x138004:0x138008 (val= on a write hit is the value BEFORE the store, s7851 r6: 0x8009983C stores 0 and reports
  the old 1.2). Port: ROGUESQ_RAND_TRACE with the s7851 snd node marks (tools/fixup_rand_trace.py) + ROGUESQ_XTRACE_MEM
  <pc>:0:80137FCC:1 at 800989D8/80098DE0/80099720/800998E8 (state at function entry).
Both reduce to the ordered list of distinct flag values with the mission tick (0x800FA730 count) at which each value ENDED
(retail: tick of the overwriting store; port: tick of the first mark that sees the next value; port lags by <=1 VI so the
tolerance is 1 tick), keeping only states that persist across >= 1 tick boundary. Verdict EXACT = same value sequence and every end tick within 1. --control drops one retail transition
and must report a mismatch."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rs64_zopen import zopen
def retail(path):
    seq, tick = [], 0
    for ln in zopen(path):
        if not ln.startswith('[hit]'): continue
        d = dict(x.split('=', 1) for x in ln.split() if '=' in x)
        if d.get('pc') == '0x800fa730': tick += 1; continue
        if d.get('addr') == '0x00137fcc' and 'val' in d:
            v = int(d['val'], 16)
            if not seq or seq[-1][0] != v: seq.append([v, tick])
            else: seq[-1][1] = tick
    return [(v, t) for v, t in seq]
def port(path):
    MK = {'800989d8', '80098de0', '80099720', '800998e8'}
    seq, tick, prev = [], 0, None
    for ln in zopen(path):
        f = ln.split()
        if len(f) < 3: continue
        if f[2] == '800fa730': tick += 1; continue
        if f[2] not in MK: continue
        m = [x for x in f if x.startswith('m=80137fcc:')]
        if not m: continue
        v = int(m[0].split(':')[1].split(',')[0], 16)
        if prev is not None and v != prev: seq.append((prev, tick))
        prev = v
    return seq
R, P = retail(sys.argv[1]), port(sys.argv[2])
def persist(seq):  # keep states that span >= 1 tick boundary (port entry marks cannot see sub-tick transients)
    out, start = [], 0
    for v, t in seq:
        if t > start and (not out or out[-1][0] != v): out.append((v, t))
        elif t > start: out[-1] = (v, t)
        start = t
    return out
R = persist([x for x in R if x[1] > 0]); P = persist([x for x in P if x[1] > 0])   # mission only
if '--control' in sys.argv and len(R) > 10: del R[len(R) // 2]
print('retail transitions', len(R), 'port transitions', len(P))
bad = None
for i in range(max(len(R), len(P))):
    r = R[i] if i < len(R) else None; p = P[i] if i < len(P) else None
    if r is None or p is None or r[0] != p[0] or abs(r[1] - p[1]) > 1:
        bad = i; break
if bad is None:
    print('VERDICT EXACT: same %d-step flag sequence, max end-tick skew %d' % (len(R), max(abs(r[1] - p[1]) for r, p in zip(R, P))))
else:
    print('VERDICT MISMATCH at step', bad)
    for j in range(max(0, bad - 3), bad + 4):
        print(' ', j, 'retail', ('%08x@%d' % R[j]) if j < len(R) else '-', 'port', ('%08x@%d' % P[j]) if j < len(P) else '-')
