#!/usr/bin/env python3
"""s5095: sync stale unsigned-base MEM_x() diagnostics in the live RecompiledFuncs tree.

MEM_x(off, base) computes (base+off) - 0xFFFFFFFF80000000 in 64 bits; a bare 0x8xxxxxxx(u)
literal zero-extends and lands 2^32 above rdram (SIGSEGV when the diagnostic's env gate is on).
The fixup/apply scripts already emit S32(); this repairs live files that predate that.
Idempotent. Usage: repair_unsigned_base_live.py [RecompiledFuncs dir]
"""
import re, sys, pathlib

d = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
LIT = r'(0[xX][89A-Fa-f][0-9A-Fa-f]{7}u?)'
OFF = r'(-?0[xX][0-9A-Fa-f]+u?)'
pat_off_base = re.compile(r'(MEM_[A-Z]+\(\s*' + OFF + r'\s*,\s*)' + LIT + r'(\s*\))')
pat_base_off = re.compile(r'(MEM_[A-Z]+\()\s*' + LIT + r'\s*,\s*' + OFF + r'(\s*\))')
total = 0
for p in sorted(d.glob("funcs_*.c")):
    s = p.read_text(errors="surrogateescape")
    s, c1 = pat_off_base.subn(lambda m: f"{m.group(1)}S32({m.group(3)}){m.group(4)}", s)
    # (base, off): same sum as (off, base), so only the literal needs S32; emit canonical order
    s, c2 = pat_base_off.subn(lambda m: f"{m.group(1)}{m.group(3)}, S32({m.group(2)}){m.group(4)}", s)
    if c1 + c2:
        p.write_text(s, errors="surrogateescape")
        print(f"{p.name}: repaired {c1 + c2}")
        total += c1 + c2
print(f"total repaired: {total}")
