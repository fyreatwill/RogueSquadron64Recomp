#!/usr/bin/env python3
"""s7318: merge ROGUESQ_S7318_BCMP tables (one per run) against tools/s7318_bcmp_sites.txt. Prints executed / never-executed sites
per function, every site with a spill operand (same / spsp / cross / speq / unm counts) and the cross examples. Exit 1 if any
cross compare was seen. Usage: s7318_bcmp_report.py <bcmp.txt>..."""
import sys, pathlib
S = {}
for l in open(pathlib.Path(__file__).resolve().parent / "s7318_bcmp_sites.txt"):
    if not l.startswith("#"): f = l.split(); S.setdefault(int(f[0]), f)
tot = {}; ex = {}; ctl = 0
for p in sys.argv[1:]:
    try: lines = open(p).read().splitlines()
    except OSError: print("missing", p); continue
    for l in lines:
        if l.startswith("#"):
            if "ctl_cross=" in l: ctl += int(l.split("ctl_cross=")[1].split()[0])
            continue
        a, _, b = l.partition("|"); f = a.split(); i = int(f[0]); v = list(map(int, f[2:]))
        tot[i] = [x + y for x, y in zip(tot.get(i, [0] * len(v)), v)]
        ex.setdefault(i, []).extend(b.split())
cols = "n nn hh same spsp cross speq unm ctl_n ctl_cross".split()
cross = sum(v[5] for v in tot.values())
print("runs=%d executed=%d/%d cross=%d ctl_cross=%d" % (len(sys.argv) - 1, len(tot), len(S), cross, ctl))
for i in sorted(tot):
    v = tot[i]
    if v[3] or v[4] or v[5] or v[6] or v[7]:
        print("  spill-operand %d %s %s %s" % (i, S[i][1], S[i][2], " ".join("%s=%d" % (c, x) for c, x in zip(cols, v) if x)), *ex.get(i, [])[:4])
un = {}
for i, f in S.items():
    if i not in tot: un[f[2]] = un.get(f[2], 0) + 1
print("never executed: %d sites: %s" % (sum(un.values()), ", ".join("%s %d" % kv for kv in sorted(un.items(), key=lambda x: -x[1]))))
sys.exit(1 if cross else 0)
