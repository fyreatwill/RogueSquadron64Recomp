#!/usr/bin/env python3
"""s4977b: emitted-C shape of jr non-$ra, grouped by register, plus neighbours of neg sltiu."""
import re, glob, collections
D = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/"
shape = collections.defaultdict(collections.Counter); ex = {}
for f in sorted(glob.glob(D + "*.c")):
    L = open(f, errors="replace").read().split("\n")
    for i, l in enumerate(L):
        m = re.match(r"\s*// (0x[0-9A-F]{8}): jr\s+(\$\w+)", l)
        if m and m.group(2) != "$ra":
            blk = " | ".join(x.strip() for x in L[i+1:i+6] if not x.strip().startswith("//"))
            k = re.sub(r"0x[0-9a-fA-F]+|\d+", "N", blk)[:110]
            shape[m.group(2)][k] += 1; ex.setdefault((m.group(2), k), (m.group(1), blk[:200]))
        if re.match(r"\s*// 0x800A4E[CD]\w: sltiu", l):
            print("NEG", "\n".join(L[i-3:i+3]))
for r, c in shape.items():
    for k, n in c.most_common(4):
        print(r, n, ex[(r, k)])
