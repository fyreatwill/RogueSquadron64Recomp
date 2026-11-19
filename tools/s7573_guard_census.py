#!/usr/bin/env python3
"""s7573 GUARD-6 fire census (docs/COMPENSATION-CHAINS.md class GUARD).

Scores game stderr logs for the six default-on GUARD levers:
  COPY_GUARD   [s5037-copy-guard] ... SKIPPED          ctl: ROGUESQ_COPY_GUARD_FORCE=1   "(FORCE control"
  PIO_GUARD    [s5062-pio-guard] ... SKIPPED           ctl: ROGUESQ_PIO_GUARD_FORCE=1    "(FORCE control"
  PI_DMA_GUARD [s5061-pi-dma-guard] ... SKIPPED        ctl: ROGUESQ_PI_DMA_GUARD_FORCE=1 "(FORCE control"
  SPAI_GUARD   [s5063-spai-guard] ... SKIPPED          ctl: ROGUESQ_SPAI_GUARD_FORCE=1   "FORCE(log-only)"
               plus [s5065-wrapper-census] <wrapper> calls=N bad=M (denominator, every power-of-two call)
  s1978 drain  [drain-timeout] (fires past 1e7 spins)  witness: [drain-exit] iters=N (margin to the 1e7 threshold)
  div-trap     [m5-keyon-table] siteK div=N guard=M    (ROGUESQ_LOG_M5_KEYON_CENSUS=1; guard = teq divisor==0 early return)

usage: s7573_guard_census.py LOG...          per-log table
       s7573_guard_census.py --retained DIR   every *.txt/*.log under DIR that carries a game-run marker
       --gate (s7658, first arg): exit 1 on any natural fire, 3 if the set carries no FORCE control row for COPY, PI_DMA
       and SPAI (a zero without its control is not a zero). Standing input: scratch/s7573/retained (filtered s7573 logs).
"""
import os, re, sys

RANGE = {"COPY": "[s5037-copy-guard]", "PIO": "[s5062-pio-guard]", "PIDMA": "[s5061-pi-dma-guard]", "SPAI": "[s5063-spai-guard]"}
MARK = ("[s5065-wrapper-census]", "[drain-exit]", "[host-start]")
CEN = re.compile(r"\[s5065-wrapper-census\] (\w+) calls=(\d+) bad=(\d+)")
DEX = re.compile(r"\[drain-exit\] call=\d+ iters=(\d+)")
KT = re.compile(r"site(\d)=0x[0-9A-F]+ div=(\d+) guard=(\d+)")


def score(path):
    r = {k: 0 for k in RANGE}; r.update({k + "_ctl": 0 for k in RANGE})
    r.update(drain_to=0, drain_max=0, drain_n=0, div=0, divguard=0, ktab=0, game=False, cen={})
    with open(path, "r", errors="replace") as f:
        for line in f:
            if '"command"' in line:      # agent transcripts quote the sources; not a game log
                return None
            if not r["game"] and any(m in line for m in MARK):
                r["game"] = True
            for k, tag in RANGE.items():
                if tag in line:
                    if "FORCE" in line: r[k + "_ctl"] += 1
                    elif "SKIPPED" in line: r[k] += 1
            m = CEN.search(line)
            if m:
                w, c, b = m.group(1), int(m.group(2)), int(m.group(3))
                pc, pb = r["cen"].get(w, (0, 0)); r["cen"][w] = (max(pc, c), max(pb, b))
            if "[drain-timeout]" in line: r["drain_to"] += 1
            m = DEX.search(line)
            if m: r["drain_n"] += 1; r["drain_max"] = max(r["drain_max"], int(m.group(1)))
            if "[m5-keyon-table]" in line:
                r["ktab"] += 1
                d = g = 0
                for s, dv, gv in KT.findall(line): d += int(dv); g += int(gv)
                r["div"], r["divguard"] = max(r["div"], d), max(r["divguard"], g)   # counters are cumulative
    return r if r["game"] else None


def row(name, r):
    cen = " ".join(f"{w}={c}/{b}" for w, (c, b) in sorted(r["cen"].items()))
    rng = " ".join(f"{k}={r[k]}(ctl{r[k+'_ctl']})" for k in RANGE)
    return (f"{name}: {rng} drain_to={r['drain_to']} drain_exit={r['drain_n']} max_iters={r['drain_max']} "
            f"keyon_tab={r['ktab']} div={r['div']} divguard={r['divguard']} census[calls/bad]: {cen}")


def main(a):
    gate = bool(a) and a[0] == "--gate"
    if gate: a = a[1:]
    if a and a[0] == "--retained":
        paths = []
        for root, _, fs in os.walk(a[1]):
            paths += [os.path.join(root, f) for f in fs if f.endswith((".txt", ".log"))]
    else:
        paths = a
    tot = None; n = 0
    for p in sorted(paths):
        try: r = score(p)
        except OSError: continue
        if r is None: continue
        n += 1
        if a and a[0] != "--retained": print(row(os.path.basename(os.path.dirname(p)) + "/" + os.path.basename(p), r))
        if tot is None: tot = {k: v for k, v in r.items() if k != "cen"}; tot["cen"] = {}
        else:
            for k, v in r.items():
                if k in ("cen", "game"): continue
                tot[k] = max(tot[k], v) if k == "drain_max" else tot[k] + v
        for w, (c, b) in r["cen"].items():
            pc, pb = tot["cen"].get(w, (0, 0)); tot["cen"][w] = (pc + c, pb + b)
    if tot is None: print("no game logs"); return 1
    print(row(f"TOTAL logs={n}", tot))
    nat = sum(tot[k] for k in RANGE) + tot["drain_to"] + tot["divguard"] + sum(b for _, b in tot["cen"].values())
    print(f"natural_fires={nat}")
    if gate:
        noctl = [k for k in ("COPY", "PIDMA", "SPAI") if tot[k + "_ctl"] == 0]
        if nat: print(f"GATE FAIL natural_fires={nat}"); return 1
        if noctl: print("GATE NO-CONTROL " + ",".join(noctl)); return 3
        print("GATE PASS natural_fires=0, controls COPY/PIDMA/SPAI fired")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
