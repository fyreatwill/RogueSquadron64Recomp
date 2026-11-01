#!/usr/bin/env python3
"""s6716: aggregate an xctrace Time Profiler export (time-profile table XML).
usage: xctrace_tp.py export.xml [--thread SUBSTR] [--under FUNCSUBSTR] [--top N]
Prints thread totals, inclusive/self per function on the chosen thread, and (with --under)
self-sample leaf addresses inside the subtree rooted at the first frame matching FUNCSUBSTR,
plus the binary load address. --dump-addrs FILE writes the root-frame addrs for line lookup."""
import sys, collections, argparse, xml.etree.ElementTree as ET
ap = argparse.ArgumentParser(); ap.add_argument('xml'); ap.add_argument('--thread', default='')
ap.add_argument('--under', default=''); ap.add_argument('--top', type=int, default=25); ap.add_argument('--dump-addrs', default=''); a = ap.parse_args()
ids = {}; frames = {}; load = None
rows = []
for ev, el in ET.iterparse(a.xml, events=('end',)):
    if el.tag in ('thread', 'binary', 'frame', 'backtrace', 'tagged-backtrace', 'thread-state', 'weight'):
        if 'id' in el.attrib: ids[el.attrib['id']] = el
    if el.tag == 'binary' and 'load-addr' in el.attrib and el.attrib.get('name') == 'RogueSquadron64Recomp': load = el.attrib['load-addr']
    if el.tag == 'row':
        def res(t):
            x = el.find(t)
            if x is None: return None
            return ids.get(x.attrib['ref'], x) if 'ref' in x.attrib else x
        th = res('thread'); bt = res('tagged-backtrace'); st = res('thread-state')
        tname = th.attrib.get('fmt', '') if th is not None else ''
        fl = []
        if bt is not None:
            b = bt.find('backtrace'); b = ids.get(b.attrib['ref'], b) if b is not None and 'ref' in b.attrib else b
            if b is not None:
                for f in b.findall('frame'):
                    f = ids.get(f.attrib['ref'], f) if 'ref' in f.attrib else f
                    fl.append((f.attrib.get('name', '?'), f.attrib.get('addr', '0')))
        rows.append((tname, st.attrib.get('fmt', '') if st is not None else '', fl))
print('load-addr', load)
tc = collections.Counter(r[0].split(' (')[0] for r in rows)
for t, n in tc.most_common(8): print(f'{n:6d} {t}')
sel = [r for r in rows if a.thread in r[0] and r[2]]
print(f'\nthread~{a.thread!r}: {len(sel)} samples')
inc = collections.Counter(); slf = collections.Counter()
for _, _, fl in sel:
    slf[fl[0][0]] += 1
    for n in set(f[0] for f in fl): inc[n] += 1
print('-- inclusive'); [print(f'{n:6d} {k[:110]}') for k, n in inc.most_common(a.top)]
print('-- self'); [print(f'{n:6d} {k[:110]}') for k, n in slf.most_common(a.top)]
if a.under:
    sub = [fl for _, _, fl in sel if any(a.under in f[0] for f in fl)]
    print(f'\n-- under {a.under!r}: {len(sub)} samples; self by leaf function')
    lf = collections.Counter(fl[0][0] for fl in sub); [print(f'{n:6d} {k[:110]}') for k, n in lf.most_common(a.top)]
    # leaf addrs attributed to the first frame of the subtree root itself or its inlined body
    ad = collections.Counter()
    for fl in sub:
        # frame directly at/below root: the frame whose name matches root, or leaf if leaf is root
        for i, f in enumerate(fl):
            if a.under in f[0]:
                ad[(f[1], 'self' if i == 0 else 'callsite')] += 1; break
    print('-- root-frame addrs (self = leaf in root; callsite = return addr of a callee)')
    for (addr, kind), n in ad.most_common(a.top * 2): print(f'{n:6d} {addr} {kind}')
    if a.dump_addrs:  # "<n> <addr> <self|callsite>" for lldb `image lookup -a` (subtract load-addr, add 0x100000000)
        with open(a.dump_addrs, 'w') as fo:
            for (addr, kind), n in ad.items(): fo.write(f'{n} {addr} {kind}\n')
