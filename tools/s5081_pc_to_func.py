#!/usr/bin/env python3
"""s5081: map recompiled guest PCs to the enclosing RECOMP_FUNC name.
Usage: s5081_pc_to_func.py PC [PC...]   (hex, e.g. 8004E470)"""
import sys, re, pathlib
D = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
want = {a.upper(): None for a in sys.argv[1:]}
for p in sorted(D.glob("funcs_*.c")):
    cur = None
    for l in p.read_text().splitlines():
        m = re.match(r'\s*RECOMP_FUNC void (\w+)\(', l)
        if m:
            cur = m.group(1)
            continue
        m = re.match(r'\s*// 0x([0-9A-F]{8}):', l)
        if m and m.group(1) in want and want[m.group(1)] is None:
            want[m.group(1)] = cur
for k, v in want.items():
    print(k, v)
