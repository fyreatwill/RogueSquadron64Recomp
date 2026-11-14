#!/usr/bin/env python3
"""s7321: class-D (24-bit truncation) view of ROGUESQ_S7318_BCMP tables (idx 512-767, tools/s7321_trunc_sites.txt).
Each hook classes (source, 0x80000000): cross = the truncated source was a spill pointer (0x81000000-0x813FFFFF), i.e. the masked
value aliases low RDRAM / heap. Prints executed / never-executed sites, every cross with examples, the control counters.
Exit 1 if any class-D cross was seen. Usage: s7321_trunc_report.py <bcmp.txt>..."""
import sys, pathlib
S = {}
for l in open(pathlib.Path(__file__).resolve().parent / "s7321_trunc_sites.txt"):
    if not l.startswith("#"): f = l.split(); S.setdefault(int(f[0]), f)
tot = {}; ex = {}
for p in sys.argv[1:]:
    for l in open(p).read().splitlines():
        if l.startswith("#"): continue
        a, _, b = l.partition("|"); f = a.split(); i = int(f[0])
        if i < 512: continue
        v = list(map(int, f[2:]))
        tot[i] = [x + y for x, y in zip(tot.get(i, [0] * len(v)), v)]
        ex.setdefault(i, []).extend(b.split())
cols = "n nn hh same spsp cross speq unm ctl_n ctl_cross".split()
T = [sum(v[k] for v in tot.values()) for k in range(10)]
print("runs=%d class-D executed=%d/%d %s" % (len(sys.argv) - 1, len(tot), len(S), " ".join("%s=%d" % (c, x) for c, x in zip(cols, T))))
for i in sorted(tot):
    v = tot[i]; f = S[i]
    print("  %s %d %s %s %s mask=%s src=%s %s" % ("CROSS" if v[5] else "ok   ", i, f[1], f[3], f[4], f[5], f[6],
          " ".join("%s=%d" % (c, x) for c, x in zip(cols, v) if x)), *ex.get(i, [])[:3])
print("never executed idx:", " ".join("%d(%s)" % (i, S[i][3]) for i in sorted(set(S) - set(tot))))
sys.exit(1 if T[5] else 0)
