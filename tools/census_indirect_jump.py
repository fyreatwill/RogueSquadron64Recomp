#!/usr/bin/env python3
"""Census of indirect jumps (jr non-ra / jalr) in generated code (s4821).

Classes: jump-table switch (jr w/ switch_error default), jalr/jr dispatch via
LOOKUP_FUNC(reg), jr/jalr $zero (LOOKUP_FUNC(0) -> get_function aborts).
Reports per-register counts and, for $zero sites, the enclosing function.
"""
from pathlib import Path
import re, sys, collections
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
fn_re = re.compile(r'^RECOMP_FUNC void (\w+)\(')
op_re = re.compile(r'// 0x([0-9A-F]{8}): (?:\.word\s+\S+\s+# )?(jr|jalr)\s+\$(\w+)')
lk_re = re.compile(r'LOOKUP_FUNC\(([^)]*)\)')
regs = collections.Counter(); zero = []; sw = 0; lk = collections.Counter(); sw_err = 0
for p in sorted(ROOT.glob("funcs_*.c")):
    fn = None
    for l in p.read_text(errors="replace").splitlines():
        m = fn_re.match(l)
        if m: fn = m.group(1)
        m = op_re.search(l)
        if m:
            a, op, r = m.groups()
            if r == 'ra' and op == 'jr': continue
            regs[(op, r)] += 1
            if r == 'zero': zero.append((a, fn, op))
        if 'switch (jr_addend' in l: sw += 1
        if 'switch_error(' in l: sw_err += 1
        m = lk_re.search(l)
        if m: lk['const' if m.group(1).startswith('0') else 'reg'] += 1
print("indirect by (op,reg):", dict(regs))
print("jump-table switches:", sw, " switch_error defaults:", sw_err)
print("LOOKUP_FUNC const/reg:", dict(lk))
print("$zero sites:", len(zero))
for a, f, op in zero: print(f"  0x{a} {op} {f}")
