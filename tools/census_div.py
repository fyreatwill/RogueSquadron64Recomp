#!/usr/bin/env python3
"""Census of integer divide sites (div/divu/ddiv/ddivu) in generated code.
Classifies the divisor: literal zero (compile-time UB) versus register, and
prints every literal-zero site with its enclosing function."""
from pathlib import Path
import re
import sys
import collections

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
FUNC = re.compile(r"\b(\w+)\(uint8_t\*\s*rdram,\s*recomp_context\*\s*ctx\)\s*\{")
DD = re.compile(r"\b(DDIVU?)\(([^,]*), ([^,]*),")
ZERO_W = re.compile(r"^(S64\(S32\(0\)\)|U32\(0\))\)")
rows = []
for p in sorted(ROOT.glob("funcs_*.c")):
    cur = ""
    for n, l in enumerate(p.read_text(errors="replace").splitlines(), 1):
        m = FUNC.search(l)
        if m:
            cur = m.group(1)
        if "lo = S32(" in l and " / " in l:
            kind = "divu" if "U32(" in l.split(" / ")[0] else "div"
            div = l.split(" / ")[1].strip()
            rows.append((p.name, n, cur, kind, "ZERO" if ZERO_W.match(div) else "reg"))
        else:
            d = DD.search(l)
            if d:
                rows.append((p.name, n, cur, d.group(1).lower(),
                             "ZERO" if d.group(3).strip() in ("S64(0)", "U64(0)", "0") else "reg"))
by = collections.Counter((r[3], r[4]) for r in rows)
print("total", len(rows), dict(by))
for r in rows:
    if r[4] == "ZERO":
        print("\t".join(map(str, r)))
print("distinct funcs", len(set(r[2] for r in rows)))
