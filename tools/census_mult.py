#!/usr/bin/env python3
"""Census of mult/multu/dmult/dmultu lowerings in generated code (s4817)."""
from pathlib import Path
import sys
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
pats = {"mult": "result = S64(S32(", "multu": "result = U64(U32(", "dmult": "DMULT(", "dmultu": "DMULTU("}
n = dict.fromkeys(pats, 0)
for p in ROOT.glob("funcs_*.c"):
    for l in p.read_text(errors="replace").splitlines():
        for k, v in pats.items():
            if v in l:
                n[k] += 1
print(n)
