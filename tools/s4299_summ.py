#!/usr/bin/env python3
"""s4299: summarise [s4299-S] rows in a run log, joined with line positions of [s4298-odd] / crash."""
import re, sys, collections
lines = open(sys.argv[1], errors="replace").read().splitlines()
rows = [(i, l) for i, l in enumerate(lines) if "[s4299-S]" in l]
print("rows", len(rows), "first line", rows[0][0] if rows else None, "last line", rows[-1][0] if rows else None, "total lines", len(lines))
for i, l in enumerate(lines):
    if "s4298-odd" in l or "CRASH" in l:
        print("evt", i, l[:200]);
        if i > 0 and sum(1 for _ in range(1)) and len([1 for j in range(i) if 'evt' in lines[j]]) > 6: break
by = collections.defaultdict(list)
for i, l in rows:
    m = re.search(r"pc=(\w+) (\w) addr=(\w+)", l)
    by[m.group(1)].append((m.group(2), m.group(3), i))
for pc, v in sorted(by.items(), key=lambda kv: kv[1][0][2]):
    addrs = sorted(set(a for _, a, _ in v))
    print(pc, v[0][0], "n=%d" % len(v), "addr", addrs[0], "..", addrs[-1], "first line", v[0][2], "last line", v[-1][2])
