#!/usr/bin/env python3
"""s7749 G6c: classify every stand-in from the LAST [s7749-life] dump (ROGUESQ_STANDINS_LOG=1, one per item every 30 s).
Class = where the item spent its on-frames: ADDED (>=1 add), CULL-OFF / CULL-FAR (reached the bucket, never accepted; dominant
view-test exit), UNLINKED-NEVER (never in the DAT grid: not grid-spawned), UNLINKED-AFTER (was linked, left the grid), COND, SPAWNED, DEAD.
Also checks the activation control: every linked->unlinked edge should spawn within 2 frames (nospawn=0).
Usage: s7749_life_tally.py LOG"""
import re, sys, collections
R = re.compile(r"\[s7749-life\] gen=(\d+) i=(\d+) item (\w+) sub (\w+) (.*)")
rows = {}
for l in open(sys.argv[1], errors="replace"):
    m = R.search(l)
    if m:
        kv = dict(x.split("=", 1) for x in m.group(5).split() if "=" in x)
        rows[(m.group(1), m.group(3))] = dict(kv, sub=m.group(4), item=m.group(3))
last_gen = max((g for g, _ in rows), key=int)
items = [v for (g, _), v in rows.items() if g == last_gen]
def cls(v):
    n = {k: int(v[k]) for k in ("add", "cull", "spawned", "unlinked", "dead", "cond", "v_off", "v_far", "v_novt", "v_pass")}
    if n["add"]: return "ADDED"
    if n["cull"]: return "CULL-FAR" if n["v_far"] >= max(n["v_off"], n["v_novt"], n["v_pass"]) else ("CULL-OFF" if n["v_off"] >= n["v_novt"] else "CULL-NOVT")
    if n["spawned"] and not (n["unlinked"] or n["cond"]): return "SPAWNED"
    if n["unlinked"]: return "UNLINKED-NEVER" if v["ever_lk"] == "0" else "UNLINKED-AFTER"
    if n["cond"]: return "COND"
    return "DEAD" if n["dead"] else "NONE"
C = collections.defaultdict(list)
for v in items: C[cls(v)].append(v)
print(f"gen={last_gen} items={len(items)} " + " ".join(f"{k}={len(C[k])}" for k in sorted(C)))
for k in sorted(C):
    xs = sorted(float(v["xzmin"]) for v in C[k])
    subs = collections.Counter(v["sub"] for v in C[k])
    ever_sp = sum(1 for v in C[k] if int(v["spawned"]))
    edges = sum(int(v["edges"]) for v in C[k]); nosp = sum(int(v["nospawn"]) for v in C[k])
    cd = sorted(float(v["cdmin"]) for v in C[k] if float(v["cdmin"]) >= 0)
    print(f"  {k}: n={len(xs)} xzmin min/med/max={xs[0]:.0f}/{xs[len(xs)//2]:.0f}/{xs[-1]:.0f} ever_spawned={ever_sp} edges={edges} nospawn={nosp} "
          f"cdmin_med={cd[len(cd)//2] if cd else -1:.0f} subs={dict(subs.most_common(6))}")
tot_e = sum(int(v["edges"]) for v in items); tot_n = sum(int(v["nospawn"]) for v in items)
print(f"activation control: edges={tot_e} nospawn={tot_n} (expect edges>0, nospawn=0)")
