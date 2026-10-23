#!/usr/bin/env python3
"""Summarise [objsnap] lines of a run.log: per id, transition chain, peak, line numbers.
usage: objsnap_summary.py run.log [run.log ...]"""
import re, sys, collections
for p in sys.argv[1:]:
    ids = collections.OrderedDict()
    with open(p, errors="replace") as f:
        for n, l in enumerate(f, 1):
            m = re.match(r"\[objsnap\] id=(\d+) (\d+)->(\d+)", l)
            if m:
                i, a, b = map(int, m.groups())
                ids.setdefault(i, []).append((n, a, b))
    print(f"== {p}: {len(ids)} ids moved")
    for i, ev in ids.items():
        peak = max(max(a, b) for _, a, b in ev)
        chain = " ".join(f"{a}>{b}" for _, a, b in ev[:12]) + (" ..." if len(ev) > 12 else "")
        print(f"  id={i} n={len(ev)} peak={peak} first_line={ev[0][0]} last_line={ev[-1][0]} :: {chain}")
