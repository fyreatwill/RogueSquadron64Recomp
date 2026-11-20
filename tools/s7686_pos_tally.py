#!/usr/bin/env python3
"""s7686: tally [s7685-pos] position matches and [s7672-ho] handoff match kinds per stand-in sub.
usage: s7686_pos_tally.py log [log...]"""
import re, sys, collections as C
pos = C.defaultdict(lambda: C.Counter()); states = C.defaultdict(set); c30w = C.defaultdict(C.Counter); csubs = C.defaultdict(C.Counter)
ho = C.defaultdict(C.Counter); dist = C.defaultdict(list)
P = re.compile(r'\[s7685-pos\] f=(\d+) state=(\w+) c34=(\w+) c30=(\w+) caller_item=(\w+) caller_sub=(\w+) standin=(\w+) sub=(\w+) d=([\d.]+) (\w+)')
H = re.compile(r'\[s7672-ho\] item (\w+) sub (\w+) why=(\S+).* match=(\w+)')
for fn in sys.argv[1:]:
    for l in open(fn, errors='replace'):
        m = P.search(l)
        if m:
            f, st, c34, c30, ci, cs, si, sub, d, v = m.groups()
            pos[sub][v] += 1; states[sub].add(st); dist[sub].append(float(d)); csubs[sub][cs] += 1
            c30w[sub]['c30==c34' if c30 == c34 else 'differ'] += 1
            if c30 == c34: c30w[sub]['w=' + c30] += 1
            continue
        m = H.search(l)
        if m: ho[m.group(2)][m.group(4)] += 1; ho[m.group(2)]['why=' + m.group(3)] += 1
subs = sorted(set(pos) | set(ho))
for s in subs:
    print(f"sub {s}: pos {dict(pos[s])} caller_states={len(states[s])} caller_sub={dict(csubs[s])} {dict(c30w[s].most_common(4))} "
          f"d={min(dist[s]) if dist[s] else '-'}..{max(dist[s]) if dist[s] else '-'} | ho {dict(ho[s])}")
print(f"total pos lines={sum(sum(c.values()) for c in pos.values())} ho lines={sum(sum(v for k,v in c.items() if not k.startswith('why')) for c in ho.values())}")
