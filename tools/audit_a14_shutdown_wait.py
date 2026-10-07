#!/usr/bin/env python3
"""A14 audit: tally slot-0 status at every shutdownMusyXVoices entry/exit
in [s2028-a11] logs. The wait loop at 0x8009BCEC only spins when status != 0
at entry, so all-zero entries mean the loop is never entered on that route.
Usage: audit_a14_shutdown_wait.py LOG [LOG...]"""
import re, sys, collections
pat = re.compile(r"edge=shutdown-(entry|exit) phase=(\d+) width=(\d+).*shutdown_call=(\d+).*status=(0x[0-9A-Fa-f]{2})")
tally = collections.Counter()
for path in sys.argv[1:]:
    with open(path, errors="replace") as f:
        for line in f:
            m = pat.search(line)
            if m:
                tally[(m[1], f"phase={m[2]}", f"w={m[3]}", f"call={m[4]}", f"status={m[5]}")] += 1
for k, v in sorted(tally.items()):
    print(v, *k)
print("spin_reachable_rows:", sum(v for k, v in tally.items() if k[0] == "entry" and k[4] != "status=0x00"))
