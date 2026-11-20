#!/usr/bin/env python3
"""s7690 G6c frame-mode slice parity: tally [s7690-par] lines (one per stand-in after 120 bucket tries, ROGUESQ_STANDINS_LOG=1).
Prints per log: items, never-added items, never-added with slice mismatches, and the last [s7690-pt] run totals.
Usage: s7690_par_tally.py LOG [LOG...]"""
import re, sys
R = re.compile(r"\[s7690-par\] item (\w+) sub (\w+) idx=(\d+) grp=(\w+) mism=(\d+) fix=(\d+) tries=(\d+) adds=(\d+)")
for p in sys.argv[1:]:
    rows = [m.groups() for m in map(R.search, open(p, errors="replace")) if m]
    pt = [l.strip() for l in open(p, errors="replace") if l.startswith("[s7690-pt]")]
    never = [r for r in rows if int(r[7]) == 0]
    nm = [r for r in never if int(r[4]) > 0]
    mi = [r for r in rows if int(r[4]) > 0]
    odd_never = sum(1 for r in never if int(r[2]) & 1)
    print(f"{p}: items={len(rows)} never_added={len(never)} (odd_idx {odd_never}) never_with_mism={len(nm)} items_with_mism={len(mi)} "
          f"added_with_mism={len(mi) - len(nm)} last={pt[-1] if pt else 'none'}")
