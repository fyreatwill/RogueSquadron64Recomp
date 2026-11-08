#!/usr/bin/env python3
"""s6960 G1e: sum [g1e-pcache] lines (ROGUESQ_G1E_PROVCACHE) per arm. usage: g1e_pcache_sum.py LOG [--skip 100]
Prints per arm: calls/s, hit %, verify wrong (vbad/vchk), mutant wrong (mbad/mchk, must be high = positive control),
key/hash/load ns and the implied budget in ms per wall second: hash saved = hits*hashns, cost = calls*keyns + loads*loadns."""
import sys, re, argparse
ap = argparse.ArgumentParser(); ap.add_argument('log'); ap.add_argument('--skip', type=int, default=100); a = ap.parse_args()
rows = [dict((k, float(v)) for k, v in re.findall(r'(\w+)=([\d.]+)', l)) for l in open(a.log, errors='replace') if l.startswith('[g1e-pcache]')]
if not rows: sys.exit('no [g1e-pcache] lines')
t0 = rows[0]['t']; rows = [r for r in rows if r['t'] - t0 >= a.skip]
for arm in sorted({r['arm'] for r in rows}):
    g = [r for r in rows if r['arm'] == arm]; n = len(g); S = lambda k: sum(r[k] for r in g); M = lambda k: sum(r[k] for r in g) / n
    print(f"arm={int(arm)} secs={n} calls/s={S('calls')/n:.0f} hit={100*S('hits')/max(S('calls'),1):.2f}% vbad={S('vbad'):.0f}/{S('vchk'):.0f} "
          f"mbad={S('mbad'):.0f}/{S('mchk'):.0f} ({100*S('mbad')/max(S('mchk'),1):.1f}%) loads/s={S('loads')/n:.0f} maskmiss={100*S('maskmiss')/max(S('loads'),1):.2f}% wrap={S('wrap'):.0f}")
    print(f"   keyns={M('keyns'):.1f} hashns={M('hashns'):.1f} loadns={M('loadns'):.1f}  saved={S('hits')/n*M('hashns')/1e6:.1f} ms/s  "
          f"cost key={S('calls')/n*M('keyns')/1e6:.1f} + load={S('loads')/n*M('loadns')/1e6:.1f} ms/s")
