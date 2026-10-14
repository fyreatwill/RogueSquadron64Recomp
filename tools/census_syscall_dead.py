#!/usr/bin/env python3
"""s4819: prove a recomp_syscall_handler site is dead-by-construction.
For each non-data-symbol syscall site, reports whether the originating word is a '.word'
(data) and whether an unconditional top-level 'return;' precedes it in the function, plus
the set of gotos emitted before that return (a goto past the return would make it live).
Usage: census_syscall_dead.py [RecompiledFuncs]"""
import re, sys
from pathlib import Path
root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
fn_re = re.compile(r'^(?:RECOMP_FUNC\s+)?void\s+(\w+)\(')
for p in sorted(root.glob("funcs_*.c")):
    L = p.read_text(errors="replace").splitlines()
    fn = None
    ret_seen = False
    gotos_before_ret = set()
    for i, l in enumerate(L):
        m = fn_re.match(l)
        if m:
            fn, ret_seen, gotos_before_ret = m.group(1), False, set()
        g = re.search(r'goto (L_\w+);', l)
        if g and not ret_seen:
            gotos_before_ret.add(g.group(1))
        if l.startswith("    return;"):
            ret_seen = True
        if "recomp_syscall_handler(" in l and fn and not fn.startswith(("data_gap", "static_", "audioCompandS16", "__OSGlobalIntMask")):
            word = ".word" in L[i - 1]
            print(f"{fn} {p.name}:{i + 1} data_word={word} top_level_return_before={ret_seen} gotos_before_return={sorted(gotos_before_ret)}")
