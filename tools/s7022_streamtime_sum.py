#!/usr/bin/env python3
"""s7022: summarise [s7022-st] lines (tools/apply_s7022_streamtime.py) per cap bucket. Uses the last K lines per cap (flight is
the tail of a hold; earlier buckets mix menus/cutscenes). usage: s7022_streamtime_sum.py <run.log> [K=6]"""
import re, sys, collections
K = int(sys.argv[2]) if len(sys.argv) > 2 else 6
rows = collections.defaultdict(list)
for l in open(sys.argv[1], errors="replace"):
    m = re.search(r"\[s7022-st\] cap=(-?\d+) (.*)", l)
    if m: rows[int(m.group(1))].append({k: float(v) for k, v in re.findall(r"(\w+)=([-\d.]+)", m.group(2))})
for cap, rs in sorted(rows.items()):
    t = rs[-K:]; avg = lambda k: sum(r[k] for r in t) / len(t)
    print(f"cap={cap:6d} lines={len(rs):3d} used={len(t)} calls/s={256/avg('span_s'):.1f} setup_us={avg('setup_us'):.1f} loop_us={avg('loop_us'):.1f} "
          f"tot_us={avg('tot_us'):.1f} cells={avg('cells'):.0f} rows={avg('rows'):.1f} ns/cell={avg('ns_per_cell'):.1f}")
    print("   tail tot_us:", " ".join(f"{r['tot_us']:.0f}" for r in t), " cells:", " ".join(f"{r['cells']:.0f}" for r in t))
