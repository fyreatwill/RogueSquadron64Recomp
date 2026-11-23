#!/usr/bin/env python3
"""s7850: SI-thread pass cadence (processPolledControllerData 0x800027C0 entries) vs mission ticks (runInMissionFrame
0x800FA730) and VIs. Port: ROGUESQ_RAND_TRACE file with the s7850 marker rows (tools/fixup_rand_trace.py; row = idx vi pc v0
[m=...]). Retail: rs64_oracle log with --watch-pc 0x800027C0 --watch-pc 0x800FA730 ([hit] x ... pc=0x...). Prints passes per
mission tick (histogram + the first ticks whose count != 2) and, for the port, passes per VI over the mission span.
usage: s7850_si_cadence.py PORT_RAND_TXT [RETAIL_ORACLE_LOG]"""
import collections, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rs64_zopen import zopen
SI, TICK = 0x800027C0, 0x800FA730
def port(path):
    ev = []
    for l in zopen(path):
        f = l.split()
        if len(f) < 4: continue
        try: pc = int(f[2], 16)
        except ValueError: continue
        if pc in (SI, TICK): ev.append((pc, int(f[1]), l))
    return ev
def retail(path):
    ev = []
    for l in zopen(path):
        if not l.startswith('[hit] x '): continue
        m = re.search(r' pc=0x([0-9a-f]{8})', l)
        if m and int(m.group(1), 16) in (SI, TICK): ev.append((int(m.group(1), 16), -1, l))
    return ev
def per_tick(ev):
    out, n, started = [], 0, False
    for pc, vi, _ in ev:
        if pc == TICK:
            if started: out.append(n)
            started, n = True, 0
        elif started: n += 1
    return out
def report(name, ev):
    pt = per_tick(ev)
    nsi = sum(1 for e in ev if e[0] == SI); nt = sum(1 for e in ev if e[0] == TICK)
    print(f'== {name}: si passes {nsi}, mission ticks {nt}')
    if not pt: return
    h = collections.Counter(pt)
    print(f'  passes between ticks: hist {dict(sorted(h.items()))}, mean {sum(pt)/len(pt):.4f} over {len(pt)} gaps')
    odd = [(i, c) for i, c in enumerate(pt) if c != 2]
    print(f'  gaps != 2: {len(odd)}; first {odd[:12]}')
    vis = [vi for pc, vi, _ in ev if vi >= 0]
    if vis:
        t = [vi for pc, vi, _ in ev if pc == TICK]; lo, hi = t[0], t[-1]
        pv = collections.Counter(vi for pc, vi, _ in ev if pc == SI and lo <= vi <= hi)
        span = range(lo, hi + 1)
        hv = collections.Counter(pv.get(v, 0) for v in span)
        print(f'  mission VIs {lo}..{hi}: passes per VI hist {dict(sorted(hv.items()))}')
        tv = collections.Counter(vi for vi in t)
        print(f'  ticks per VI hist {dict(sorted(collections.Counter(tv.get(v, 0) for v in span).items()))}')
P = port(sys.argv[1]); report('port', P)
if len(sys.argv) > 2: report('retail', retail(sys.argv[2]))
