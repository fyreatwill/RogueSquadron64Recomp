#!/usr/bin/env python3
"""s7585 class LK: diff two `heap -s -q <pid>` tables (MallocStackLogging=lite labels blocks by allocating function).
usage: s7585_heapdiff.py early.txt late.txt [seconds_between] -> rows sorted by byte growth: dBYTES dCOUNT MB/s CLASS BINARY"""
import re, sys
def load(p):
    d = {}
    for ln in open(p, errors="replace"):
        m = re.match(r"\s*(\d+)\s+(\d+)\s+([\d.]+)\s+(.+?)\s{2,}(\S*)\s*(\S*)\s*$", ln)
        if m:
            k = (m.group(4).strip(), m.group(6) or m.group(5))
            c, b = d.get(k, (0, 0)); d[k] = (c + int(m.group(1)), b + int(m.group(2)))
    return d
a, b = load(sys.argv[1]), load(sys.argv[2]); dt = float(sys.argv[3]) if len(sys.argv) > 3 else 0
rows = sorted(((b.get(k, (0, 0))[1] - a.get(k, (0, 0))[1], b.get(k, (0, 0))[0] - a.get(k, (0, 0))[0], k) for k in set(a) | set(b)), reverse=True)
tot = sum(r[0] for r in rows); print(f"total dBYTES={tot} ({tot/2**20:.1f} MB{'' if not dt else f', {tot/2**20/dt:.3f} MB/s'}) classes={len(rows)}")
for db, dc, k in rows[:20]:
    print(f"{db:12d} {dc:9d} {db/2**20/dt if dt else 0:7.3f} {k[0][:70]:70s} {k[1]}")
