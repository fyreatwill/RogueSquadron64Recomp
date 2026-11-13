#!/usr/bin/env python3
"""s7283 G5c: bin [s7283-mtl] commit-census lines (ROGUESQ_MTL_COMMITS=1) by the s7277 toggle windows.
usage: python3 tools/s7283_commit_census.py <TAG> [...]   (reads scratch/agent/m6/g1_lvl*s7009<TAG>/*.log + scratch/s7277/<TAG>.toggle)"""
import glob, re, sys
for tag in sys.argv[1:]:
    ev = []
    for ln in open(f"scratch/s7277/{tag}.toggle"):
        p = ln.split()
        if len(p) == 2 and p[0] in ("on", "off"): ev.append((float(p[1]), p[0]))
    ev.sort()
    def state(t):
        s = "pre"
        for et, e in ev:
            if et <= t: s = e
        return s
    rows = {}
    pat = re.compile(r"\[s7283-mtl\] t=([\d.]+) dt=([\d.]+) presents=(\d+) exec=(\d+) commits/present=([\d.]+) wait=([\d.]+) waitEmpty=([\d.]+) list=([\d.]+) acq=([\d.]+) pres=([\d.]+) skipped=([\d.]+) skip=(\d)")
    lines = [ln for f in glob.glob(f"scratch/agent/m6/g1_lvl*s7009{tag}/*.log") for ln in open(f, errors="replace")]
    for ln in lines:
        m = pat.search(ln)
        if not m: continue
        t, dt = float(m[1]), float(m[2])
        st = state(t - dt / 2)
        r = rows.setdefault(st, [0, 0.0, 0, 0, [0.0] * 6])
        n = int(m[3]); r[0] += 1; r[1] += dt; r[2] += n; r[3] += int(m[4])
        for i, k in enumerate((6, 7, 8, 9, 10, 11)): r[4][i] += float(m[k]) * n
        skip = m[12]
    print(f"== {tag} (skip={skip if rows else '?'})")
    print("state  rows  sec   pres/s  exec/pres  commits/pres  wait  waitEmpty  list  acq  pres  skipped")
    for st, (k, sec, n, x, s) in sorted(rows.items()):
        n1 = max(n, 1)
        print(f"{st:5} {k:5} {sec:5.0f} {n/sec:7.1f} {x/n1:9.2f} {sum(s[i] for i in (0,2,3,4))/n1:12.2f} " + " ".join(f"{v/n1:5.2f}" for v in s))
