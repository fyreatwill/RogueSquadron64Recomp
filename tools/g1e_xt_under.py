#!/usr/bin/env python3
"""s6956 G1e: inclusive profile UNDER an anchor frame from an `xctrace export` time-profile XML.
usage: ANCHOR=rs64_dpc_defer_end_impl [THREAD='Gfx Thread'] g1e_xt_under.py T.xml
Export: xctrace export --input T.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="time-profile"]' > T.xml
For samples whose backtrace contains ANCHOR (substring of a frame name), prints:
  - anchor share of the thread's samples (positive control: must be > 0 and sit near com/sd_wall from the task ring),
  - inclusive counts of every frame ABOVE the anchor (callee side), top 40,
  - leaf histogram of those samples, top 25."""
import os, sys, collections, xml.etree.ElementTree as ET
TH = os.environ.get('THREAD', 'Gfx Thread'); AN = os.environ.get('ANCHOR', 'rs64_dpc_defer_end_impl')
ids = {}; tot = 0; hit = 0; inc = collections.Counter(); leaf = collections.Counter()
def res(e):
    r = e.get('ref'); return ids.get(r, e) if r else e
for ev, e in ET.iterparse(sys.argv[1], events=('end',)):
    i = e.get('id')
    if i: ids[i] = e
    if e.tag != 'row': continue
    bt = None; th = None
    for c in e:
        c2 = res(c)
        if c2.tag == 'tagged-backtrace':
            for g in c2:
                g = res(g)
                if g.tag == 'backtrace': bt = g
        if c2.tag == 'backtrace': bt = c2
        if c2.tag == 'thread': th = c2.get('fmt')
    if bt is None or th is None or TH not in th: continue
    fr = [(res(f).get('name') or res(f).get('addr') or '?') for f in bt if res(f).tag == 'frame']
    if not fr: continue
    tot += 1
    k = next((j for j, n in enumerate(fr) if AN in n), None)
    if k is None: continue
    hit += 1; leaf[fr[0]] += 1
    for n in set(fr[:k]): inc[n] += 1
print(f"thread~'{TH}' samples={tot} under '{AN}'={hit} ({100.0 * hit / max(tot, 1):.1f}%)")
print('# inclusive (callee side of anchor)')
for n, c in inc.most_common(40): print(f"{c:7d} {100.0 * c / max(hit, 1):5.1f}% {n[:150]}")
print('# leaves')
for n, c in leaf.most_common(25): print(f"{c:7d} {100.0 * c / max(hit, 1):5.1f}% {n[:150]}")
