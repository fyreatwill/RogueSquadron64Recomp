#!/usr/bin/env python3
"""s7587 class OW: tally OBJC_DEBUG_MISSING_POOLS lines per arm log by class (objects autoreleased with no pool = implicit-pool
entries that never drain on the RT64 threads). usage: python3 tools/s7587_missing_pools.py <log> [<log> ...]"""
import re, sys, collections
rx = re.compile(r'MISSING POOLS: \(0x[0-9a-f]+\) Object 0x[0-9a-f]+ of class (\S+) autoreleased')
for p in sys.argv[1:]:
    c = collections.Counter(); n = 0
    with open(p, errors='replace') as f:
        for l in f:
            m = rx.search(l)
            if m: c[m.group(1)] += 1; n += 1
    plant = c.get('MTLRenderPassDescriptorInternal', 0)
    print(f"{p}: missing_pool_objs={n} plant_rpd={plant} classes={len(c)}")
    for k, v in c.most_common(15): print(f"  {v:9d} {k}")
