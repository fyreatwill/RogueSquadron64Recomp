#!/usr/bin/env python3
"""s6820 G3: summarise NPC-creation rows (tag b7000000, tools/fixup_rand_trace.py spawn bt mark) in rand traces.
Per entry PC: call count, distinct $a0, VI-interval histogram, backtrace chains (first 6 frames) with counts.
Then for createAndInitObject (0x800EC588) per creating handler: creates, distinct objects, creates per game second
(VI span / 60 at 30 Hz-on-60 VI and at FPS60 alike: one VI = 1/60 s of wall and game time while the game holds 60/30),
and the per-object re-create interval histogram in VI.
Usage: g3_spawn_bt.py TRACE [TRACE...]"""
import collections, sys
for fn in sys.argv[1:]:
    rows = collections.defaultdict(list)
    for l in open(fn):
        p = l.split()
        if len(p) >= 6 and p[2] == "b7000000":
            rows[p[3]].append((int(p[1]), p[4], p[5][3:]))
    print(f"== {fn}")
    for pc, r in sorted(rows.items()):
        vis = sorted(set(v for v, _, _ in r))
        d = collections.Counter(b - a for a, b in zip(vis, vis[1:]))
        print(f" pc {pc}: {len(r)} calls, {len(set(a for _, a, _ in r))} distinct a0, VI {vis[0] if vis else '-'}..{vis[-1] if vis else '-'}, dVI {d.most_common(5)}")
        for chain, n in collections.Counter("<".join(b.split("<")[:6]) for _, _, b in r).most_common(6):
            print(f"   {n:5d}  {chain}")
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    for v, a, b in rows.get("800ec588", []):
        h = b.split("<")[1] if "<" in b else "?"
        per[h][a].append(v)
    for h, objs in sorted(per.items(), key=lambda kv: -sum(len(x) for x in kv[1].values())):
        vs = sorted(v for x in objs.values() for v in x)
        span = (vs[-1] - vs[0]) / 60.0 if len(vs) > 1 else 0
        d = collections.Counter(b - a for x in objs.values() for a, b in zip(x, x[1:]))
        print(f"  {h:28s} creates {len(vs):4d} objs {len(objs):3d} per_s {len(vs) / span if span else 0:5.2f} recreate dVI {d.most_common(4)}")
