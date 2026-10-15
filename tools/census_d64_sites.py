#!/usr/bin/env python3
"""s4975: classify every ddiv/ddivu/dmult/dmultu site in generated code.
For each unique address with a non-$zero,$zero operand pair, print the enclosing
function and whether it is a plausible code region (neighbour instructions)."""
import re, glob, sys
D = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/"
pat = re.compile(r"^\s*// (0x[0-9A-F]{8}): (ddivu?|dmultu?)\s+(.*)$")
fn_pat = re.compile(r"^(?:RECOMP_FUNC\s+)?void\s+(\w+)\(")
seen = {}
for f in sorted(glob.glob(D + "*.c")):
    cur = None
    lines = open(f, errors="replace").read().splitlines()
    for i, l in enumerate(lines):
        m = fn_pat.match(l)
        if m:
            cur = m.group(1)
        m = pat.match(l)
        if m and m.group(1) not in seen:
            addr, op, ops = m.groups()
            ops = ops.strip()
            isword = any(".word" in x for x in lines[max(0, i - 2):i + 1])
            seen[addr] = (op, ops, cur, f.split("/")[-1], isword)
for a, (op, ops, fn, f, w) in sorted(seen.items()):
    if ops.replace(" ", "") in ("$zero,$zero",):
        continue
    print(a, op, ops, fn, f, "WORD" if w else "")
print("total unique sites", len(seen), file=sys.stderr)
