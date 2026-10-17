#!/usr/bin/env python3
"""s5081: per-window deltas of [watch-wr #n] census entries (pc@physaddr:count) for the mission
object range 0x138458..0x1384C0 and pointer 0x138D1C.  Usage: s5081_wr_windows.py run.log keys.log"""
import re, sys
wr = {}
for l in open(sys.argv[1], 'rb').read().decode('latin1').splitlines():
    m = re.match(r'\[watch-wr #(\d+)\](.*)', l)
    if m:
        wr[int(m.group(1))] = {(t.split('@')[0], t.split('@')[1].split(':')[0]): int(t.split(':')[1])
                               for t in m.group(2).split()}
ns = sorted(wr)
marks = {}
for l in open(sys.argv[2]):
    m = re.match(r'MARK (\w+) watchlines=(\d+)', l)
    if m:
        marks[m.group(1)] = int(m.group(2))
def at(n):
    k = max([x for x in ns if x <= n] or [ns[0]])
    return wr[k]
keys = set()
for d in wr.values():
    keys |= set(d)
names = list(marks)
print("marks", marks)
for k in sorted(keys):
    a = int(k[1], 16)
    if not (0x138458 <= a < 0x1384C0 or a == 0x138D1C):
        continue
    v = [at(marks[x]).get(k, 0) for x in names]
    print(k, "deltas", [v[i + 1] - v[i] for i in range(len(v) - 1)], "total", v[-1])
