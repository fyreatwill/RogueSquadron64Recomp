#!/usr/bin/env python3
"""s6132 G1d: replace the literal 8 MB top-of-RAM bound (0x80800000u) in generated funcs_*.c with RS64_RAM_TOP
(runtime variable, = 0x80000000 + osMemSize; recomp.h). Idempotent. Usage: fixup_ramtop.py <RecompiledFuncs dir>"""
import sys, pathlib, re
PAT = re.compile(r"0x80800000u(?![lL])")
n = 0
for p in sorted(pathlib.Path(sys.argv[1]).glob("funcs_*.c")):
    s = p.read_text(errors="replace")
    t, k = PAT.subn("RS64_RAM_TOP", s)
    if k:
        n += k; p.write_text(t)
print(f"[s6132] fixup_ramtop: {n} literal 8MB bounds -> RS64_RAM_TOP")
