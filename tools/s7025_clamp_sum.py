#!/usr/bin/env python3
"""s7025: summarise [s7025-cl] (clampGridCellLookup split) beside [s7024-gv] b1 per 256-call bucket line, in time order.
Per-call budget of one clamp call (ns): ent (tick/dispatch) + get + val (per hit) + create share (cr_n*cr_ns/cl_n) + rest.
Prints early/late thirds and Pearson r of cl_ns against each term. Usage: s7025_clamp_sum.py run.log"""
import re, sys, statistics as st
rows = []; gv = []
for l in open(sys.argv[1], errors="replace"):
    if l.startswith("[s7024-gv]"):
        m = re.search(r"b1=([\d.]+)/([\d.]+)ns", l); m2 = re.search(r"b2=([\d.]+)/([\d.]+)ns", l)
        gv.append((float(m.group(1)) if m else 0, float(m.group(2)) if m else 0, float(m2.group(2)) if m2 else 0))
    elif l.startswith("[s7025-cl]"):
        d = dict(re.findall(r"(\w+)=([-\d.]+)", l)); d = {k: float(v) for k, v in d.items()}
        d["b1_n"], d["b1_ns"], d["b2_ns"] = gv[-1] if gv else (0, 0, 0)
        cl = d["cl_n"] or 1
        d["cr_share"] = d["cr_n"] * d["cr_ns"] / cl
        d["pre_share"] = d["pre_n"] * d["pre_ns"] / cl
        d["val_share"] = d["hit"] * d["val_ns"] / cl
        d["get_share"] = d["pre_n"] * d["get_ns"] / cl
        d["ent_share"] = d["pre_n"] * d["ent_ns"] / cl
        d["snap_share"] = d["snap_n"] * d["snap_us"] * 1e3 / cl
        d["rest"] = d["cl_ns"] - d["cr_share"] - d["pre_share"]
        rows.append(d)
K = ["b1_n", "b1_ns", "b2_ns", "cl_n", "cl_ns", "pre_share", "ent_share", "get_share", "val_share", "snap_share", "cr_n", "cr_ns", "cr_share", "rest", "hit", "miss", "ival", "r_mean", "r_max", "r_step", "r_hi"]
print("rows", len(rows))
print(" ".join(f"{k:>9}" for k in K))
for i, d in enumerate(rows):
    if i % max(1, len(rows) // 20) == 0: print(" ".join(f"{d.get(k, 0):9.1f}" for k in K))
n = len(rows) // 3
if n:
    for name, part in (("early", rows[:n]), ("late", rows[-n:])):
        print(f"{name:5}", " ".join(f"{k}={st.mean(d[k] for d in part):.1f}" for k in K))
    def r(a, b):
        xa = [d[a] for d in rows]; xb = [d[b] for d in rows]
        try: return st.correlation(xa, xb)
        except Exception: return float("nan")
    print("corr(cl_ns, .):", " ".join(f"{k}={r('cl_ns', k):+.2f}" for k in K if k != "cl_ns"))
