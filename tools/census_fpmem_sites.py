#!/usr/bin/env python3
"""s4976: classify ldc1/sdc1 sites by base register and 8-byte offset alignment.
Prints the sites whose immediate offset is not a multiple of 8 (candidates for
unaligned or data-as-code), with the enclosing line context left to the reader."""
import re, glob
D = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/"
pat = re.compile(r"\s*// (0x[0-9A-F]{8}): ([ls]dc1)\s+\$f\d+, (-?)(0x[0-9A-Fa-f]+|\d+)\((\$\w+)\)")
seen = {}
for f in sorted(glob.glob(D + "*.c")):
    for l in open(f, errors="replace"):
        m = pat.match(l)
        if m and m.group(1) not in seen:
            a, op, sg, off, base = m.groups()
            seen[a] = (op, int(off, 0) * (-1 if sg else 1), base, f.split("/")[-1])
odd = {a: v for a, v in seen.items() if v[1] % 8}
print("unique sites", len(seen), "misaligned-offset", len(odd))
for a, v in sorted(odd.items()):
    print(a, *v)
