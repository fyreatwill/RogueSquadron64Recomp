#!/usr/bin/env python3
"""s6132 G1d: replace the literal 8 MB top-of-RAM bound (0x80800000u) in generated funcs_*.c with RS64_RAM_TOP
(runtime variable, = 0x80000000 + osMemSize; recomp.h). Idempotent. Usage: fixup_ramtop.py <RecompiledFuncs dir>
s7337: also the 64-bit spelling (0x80800000ull -> ((uint64_t)RS64_RAM_TOP)); it slipped past the u-only pattern.
Scripts applied straight to the live tree after a regen bypass the vendored fixer's final call: re-run this, or
tools/s7337_bound_census.py (exit 1) catches what is left."""
import sys, pathlib, re
PAT = re.compile(r"0x80800000u(?![lL])")
PAT64 = re.compile(r"0x80800000(?:ull|ULL|llu|LLU)\b")
n = 0
for p in sorted(pathlib.Path(sys.argv[1]).glob("funcs_*.c")):
    s = p.read_text(errors="replace")
    t, k = PAT.subn("RS64_RAM_TOP", s)
    t, k2 = PAT64.subn("((uint64_t)RS64_RAM_TOP)", t)
    if k or k2:
        n += k + k2; p.write_text(t)
print(f"[s6132] fixup_ramtop: {n} literal 8MB bounds -> RS64_RAM_TOP")
