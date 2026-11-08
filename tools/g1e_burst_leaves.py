#!/usr/bin/env python3
"""s6963 G1e: name the guest code in the periodic game-thread CPU bursts. Reads an `xctrace export` time-profile XML,
keeps samples of the busiest '[Game]' thread (or THREAD=<substring>), buckets them per wall second of the trace, splits
seconds into burst (samples >= --hi x median) and quiet (<= median), and prints, per group, the share of each function
(first frame inside the game binary, i.e. recompiled guest code or runtime) plus the burst-minus-quiet delta in ms/s.
Control: the per-second sample count must show the same 8 s periodicity as [g1b-gt] thread-8 cpu (printed as a row).
usage: g1e_burst_leaves.py XML [--hi 1.6] [--top 25] [--depth 6]"""
import sys, argparse, collections, statistics as st, xml.etree.ElementTree as ET, os
ap = argparse.ArgumentParser(); ap.add_argument('xml'); ap.add_argument('--hi', type=float, default=1.6)
ap.add_argument('--top', type=int, default=25); ap.add_argument('--depth', type=int, default=6); a = ap.parse_args()
ids = {}
def res(e):
    r = e.get('ref'); return ids.get(r, e) if r else e
rows = []  # (thread, t_ns, weight_ns, [frame names in binary...], leaf)
for ev, e in ET.iterparse(a.xml, events=('end',)):
    i = e.get('id')
    if i: ids[i] = e
    if e.tag != 'row': continue
    t = th = w = None; bt = None
    for c in e:
        c2 = res(c)
        if c2.tag == 'sample-time': t = int(c2.text)
        elif c2.tag == 'thread': th = c2.get('fmt', '').split(' (RogueSquadron64Recomp')[0]
        elif c2.tag == 'weight': w = int(c2.text)
        elif c2.tag == 'tagged-backtrace':
            for g in c2:
                g = res(g)
                if g.tag == 'backtrace': bt = g
    if t is None or bt is None: continue
    fr = []
    for f in bt:
        f = res(f)
        if f.tag != 'frame': continue
        b = None
        for x in f:
            x = res(x)
            if x.tag == 'binary': b = x.get('name')
        fr.append((f.get('name') or f.get('addr'), b))
    rows.append((th, t, w or 1000000, fr))
TH = os.environ.get('THREAD')
cnt = collections.Counter(r[0] for r in rows if (TH and TH in r[0]) or (not TH and r[0].startswith('[Game]')))
gth = cnt.most_common(1)[0][0]
print('threads:', cnt.most_common(5)); print('using', gth)
G = [r for r in rows if r[0] == gth]
t0 = min(r[1] for r in G)
per = collections.defaultdict(list)
for r in G: per[(r[1] - t0) // 1_000_000_000].append(r)
secs = sorted(per); ms = {s: sum(r[2] for r in per[s]) / 1e6 for s in secs}
print('per-second ms:', ' '.join(f'{s}:{ms[s]:.0f}' for s in secs))
med = st.median(ms.values()); B = [s for s in secs if ms[s] >= a.hi * med]; Q = [s for s in secs if ms[s] <= med]
print(f'median {med:.0f} ms/s; burst secs {B} quiet n={len(Q)}')
def fn(fr):
    out = []
    for n, b in fr:
        if b == 'RogueSquadron64Recomp': out.append(n)
        if len(out) >= a.depth: break
    return out
def hist(ss, k):
    c = collections.Counter()
    for s in ss:
        for r in per[s]:
            f = fn(r[3])
            if len(f) > k: c[f[k]] += r[2] / 1e6
    return {n: v / max(1, len(ss)) for n, v in c.items()}
for k, lab in ((0, 'leaf (first game-binary frame)'), (1, 'caller 1'), (2, 'caller 2')):
    hb, hq = hist(B, k), hist(Q, k)
    print(f'--- {lab}: ms/s burst | quiet | delta')
    for n in sorted(set(hb) | set(hq), key=lambda n: -(hb.get(n, 0) - hq.get(n, 0)))[:a.top]:
        print(f'{hb.get(n,0):8.1f} {hq.get(n,0):8.1f} {hb.get(n,0)-hq.get(n,0):8.1f}  {n}')
