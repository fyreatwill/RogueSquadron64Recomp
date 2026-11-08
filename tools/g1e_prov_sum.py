#!/usr/bin/env python3
"""s6959: summarise [g1e-prov] per-second lines (ROGUESQ_G1E_PROV=stat) over a time window. usage: g1e_prov_sum.py log [t_from_rel] [t_to_rel]"""
import re, sys
lines = [l for l in open(sys.argv[1], errors='replace') if l.startswith('[g1e-prov]')]
rows = [dict((k, float(v)) for k, v in re.findall(r'(\w+)=([-\d.]+)', l)) for l in lines]
if not rows: sys.exit('no [g1e-prov] lines')
t0 = rows[0]['t']; lo = float(sys.argv[2]) if len(sys.argv) > 2 else 0; hi = float(sys.argv[3]) if len(sys.argv) > 3 else 1e9
sel = [r for r in rows if lo <= r['t'] - t0 < hi]
S = lambda k: sum(r[k] for r in sel)
c = S('calls'); n = len(sel)
print(f"seconds={n} calls={c:.0f} ({c/max(n,1):.0f}/s) ci4={S('ci4')/c:.1%}")
for a in ('A', 'S', 'M1', 'M2'):
    h = S('hit' + a); b = S('bad' + a)
    print(f"  arm {a:2}: hit {h/c:.2%}  bad {b:.0f} ({b/max(h,1):.2%} of hits)")
ts = S('tsamp')
key = sum(r['keyns'] * r['tsamp'] for r in sel) / max(ts, 1); hs = sum(r['hashns'] * r['tsamp'] for r in sel) / max(ts, 1)
print(f"  key {key:.1f} ns vs hash {hs:.1f} ns per call (ratio {key/max(hs,1e-9):.2f}); runs/call {S('runs')/c:.1f} words/call {S('words')/c:.1f}")
L = S('loads'); print(f"  loads {L/max(n,1):.0f}/s srcchg {S('srcchg')/max(L,1):.3%} maskmiss {S('maskmiss')/max(L,1):.3%} partial-word updates/load {S('partial')/max(L,1):.2f}")
