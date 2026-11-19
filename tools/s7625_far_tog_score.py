#!/usr/bin/env python3
"""s7625: split [standins-why] per-second tallies by the ROGUESQ_STANDINS_FAR=tog window (the [standins-s] line that follows
each [standins-why] line carries faron=<n>: >0 = widened-far second, 0 = retail-far second) and sum each exit per arm.
usage: s7625_far_tog_score.py LOG [LOG...]"""
import re, sys, collections
for log in sys.argv[1:]:
    acc = {True: collections.Counter(), False: collections.Counter()}; nwin = collections.Counter(); pend = None
    for ln in open(log, errors="replace"):
        if ln.startswith("[standins-why]"):
            pend = {k: float(v) for k, v in re.findall(r"(\w+)=([\d.]+)", ln)}
        elif ln.startswith("[standins-s]") and pend is not None:
            m = re.search(r"faron=(\d+)", ln); on = bool(m and int(m.group(1)) > 0)
            nwin[on] += 1
            for k, v in pend.items():
                if k not in ("dmin", "dmed", "dmax"): acc[on][k] += int(v)
            acc[on]["dmax_max"] = max(acc[on]["dmax_max"], int(pend.get("dmax", 0)))
            pend = None
    for on in (False, True):
        c = acc[on]; calls = max(1, c["calls"])
        rest = " ".join(f"{k}={v}" for k, v in sorted(c.items()) if k not in ("calls", "pass", "added"))
        print(f"{log.split('/')[-1]} far={'dd' if on else 'retail'} windows={nwin[on]} calls={c['calls']} pass={c['pass']} "
              f"rate={c['pass'] / calls:.4f} added={c['added']} {rest}")
