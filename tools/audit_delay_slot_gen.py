#!/usr/bin/env python3
"""s5345: for each hazard site, check the generated C evaluates the branch
condition before the delay-slot write.  Result classes: ok (the first code
line after the branch comment is `if (`), other (anything else; listed),
missing (no generated comment for that address)."""
import re, sys, glob, collections

sites = [l.split() for l in open(sys.argv[1])]
gen = {}
for f in sorted(glob.glob(sys.argv[2] + "/funcs_*.c")):
    L = open(f).read().split("\n")
    for i, l in enumerate(L):
        m = re.match(r"\s*// 0x([0-9A-F]{8}): (\w+)", l)
        if m:
            gen.setdefault(int(m.group(1), 16), []).append((L, i, m.group(2)))

res = collections.Counter()
bad = []
for s in sites:
    a = int(s[0], 16)
    mn = s[3]
    if a not in gen:
        res["missing"] += 1
        bad.append((s[0], mn, "missing"))
        continue
    cls = "nomatch"
    for L, i, m in gen[a]:
        if m != mn:
            continue
        j = i + 1
        while j < len(L) and not L[j].strip():
            j += 1
        nxt = L[j].strip() if j < len(L) else ""
        cls = "ok" if nxt.startswith("if (") else "other"
        if cls != "ok":
            bad.append((s[0], mn, nxt[:60]))
            break
    res[cls] += 1
print(dict(res))
for b in bad[:40]:
    print(b)
