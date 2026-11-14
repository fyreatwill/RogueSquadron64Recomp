#!/usr/bin/env python3
"""s7320: class-C (field pointer difference) view of ROGUESQ_S7318_BCMP tables (idx >= 256, tools/s7320_bdiff_sites.txt).
Prints executed / never-executed sites, every site with a spill operand (same / spsp / cross / speq / unm) with examples, and the
control counters. Exit 1 if any class-C cross subtraction (spill minus 0x80xxxxxx or the reverse) was seen.
Usage: s7320_bdiff_report.py <bcmp.txt>..."""
import sys, pathlib
S = {}
for l in open(pathlib.Path(__file__).resolve().parent / "s7320_bdiff_sites.txt"):
    if not l.startswith("#"): f = l.split(); S.setdefault(int(f[0]), f)
tot = {}; ex = {}
for p in sys.argv[1:]:
    for l in open(p).read().splitlines():
        if l.startswith("#"): continue
        a, _, b = l.partition("|"); f = a.split(); i = int(f[0])
        if i < 256: continue
        v = list(map(int, f[2:]))
        tot[i] = [x + y for x, y in zip(tot.get(i, [0] * len(v)), v)]
        ex.setdefault(i, []).extend(b.split())
cols = "n nn hh same spsp cross speq unm ctl_n ctl_cross".split()
T = [sum(v[k] for v in tot.values()) for k in range(10)]
print("runs=%d class-C executed=%d/%d %s" % (len(sys.argv) - 1, len(tot), len(S), " ".join("%s=%d" % (c, x) for c, x in zip(cols, T))))
for i in sorted(tot):
    v = tot[i]
    if any(v[3:8]):
        print("  spill-operand %d %s %s %s %s" % (i, S[i][1], S[i][2], S[i][7], " ".join("%s=%d" % (c, x) for c, x in zip(cols, v) if x)), *ex.get(i, [])[:3])
un = {}
for i, f in S.items():
    if i not in tot: un[f[2]] = un.get(f[2], 0) + 1
print("never executed: %d sites: %s" % (sum(un.values()), ", ".join("%s %d" % kv for kv in sorted(un.items(), key=lambda x: -x[1]))))
print("never-executed idx:", " ".join(str(i) for i in sorted(set(S) - set(tot))))
sys.exit(1 if T[5] else 0)
