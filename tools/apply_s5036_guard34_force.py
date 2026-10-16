#!/usr/bin/env python3
"""s5036: add ROGUESQ_FORCE_ALLOC_TAIL_GUARD3 / _GUARD4 (log-only positive controls) to the live
alloc-tail guard3/guard4 blocks (same idea as s5034 guard2).  Idempotent.

ORIGIN: not a mitigation. The guards already exist; this only lets the census prove they are
instrumented. Force makes the block LOG every pass (with ROGUESQ_LOG_ALLOC_TAIL_GUARDn=1) but the
goto is taken only when the original predicate is true.  The predicate is evaluated exactly once
(guard3 variants carry a ++s3285_walk side effect).
Usage: apply_s5036_guard34_force.py [RecompiledFuncs dir]
"""
import re, sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
pat = re.compile(
    r'^( +)if \(((?:\w+_lo|\w+_hi)[^\n]*)\) \{\n'
    r'( +if \(s_alloc_tail_guard([34])_enabled\) \{\n.*?\n +\}\n)'
    r' +goto (\w+);\n', re.S | re.M)
tot = {3: 0, 4: 0}
def rep(m):
    ind, cond, blk, g, lab = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
    tot[int(g)] += 1
    return (f'{ind}static int s_alloc_tail_guard{g}_force = -1;\n'
            f'{ind}if (s_alloc_tail_guard{g}_force < 0) {{ const char* e = getenv("ROGUESQ_FORCE_ALLOC_TAIL_GUARD{g}"); s_alloc_tail_guard{g}_force = (e && e[0] && e[0] != \'0\') ? 1 : 0; }}\n'
            f'{ind}int s_alloc_tail_guard{g}_bad = ({cond});\n'
            f'{ind}if (s_alloc_tail_guard{g}_bad || s_alloc_tail_guard{g}_force) {{\n'
            f'{blk}'
            f'{ind}    if (s_alloc_tail_guard{g}_bad) goto {lab};  // force = log only\n')
for p in sorted(D.glob("funcs_*.c")):
    t = p.read_text()
    if 's_alloc_tail_guard3_enabled' not in t and 's_alloc_tail_guard4_enabled' not in t:
        continue
    t2 = pat.sub(rep, t)
    if t2 != t:
        p.write_text(t2)
print("patched guard3=%d guard4=%d" % (tot[3], tot[4]))
