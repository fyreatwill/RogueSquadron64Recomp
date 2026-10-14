#!/usr/bin/env python3
"""Census of float->int conversion sites (TRUNC_W_S/D, CVT_W_S/D) in generated code.
For each site, find the FPR destination and classify what the next lines do with it:
  addr  - fed (via mfc1 move) into an ADD32/memory-address expression
  store - stored straight to memory (swc1 / MEM_W store)
  other - anything else / no use within WINDOW lines
Usage: census_f2i.py [RecompiledFuncs dir]"""
from pathlib import Path
import re
import sys
import collections

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
FUNC = re.compile(r"\b(\w+)\(uint8_t\*\s*rdram,\s*recomp_context\*\s*ctx\)\s*\{")
SITE = re.compile(r"(ctx->f(\d+)\.\w+)\s*=\s*(TRUNC_W_[SD]|CVT_W_[SD])\(")
WINDOW = 6
rows = []
for p in sorted(ROOT.glob("funcs_*.c")):
    lines = p.read_text(errors="replace").splitlines()
    cur = ""
    for n, l in enumerate(lines):
        m = FUNC.search(l)
        if m:
            cur = m.group(1)
        s = SITE.search(l)
        if not s:
            continue
        fn = "f" + s.group(2)
        cls = "other"
        for k in range(n + 1, min(n + 1 + WINDOW, len(lines))):
            t = lines[k]
            if re.search(r"= ctx->%s\.\w+;" % fn, t) or re.search(r"= .*ctx->%s\.\w+" % fn, t):
                # moved to a GPR (mfc1) or stored
                if "MEM_" in t or "SW(" in t:
                    cls = "store"
                    break
                g = re.match(r"\s*(ctx->r\d+)\s*=", t)
                if g:
                    gpr = g.group(1)
                    for j in range(k + 1, min(k + 1 + WINDOW, len(lines))):
                        u = lines[j]
                        if gpr in u and ("ADD32" in u or "MEM_" in u) and not u.strip().startswith(gpr + " ="):
                            cls = "addr"
                            break
                        if gpr in u and "MEM_W(" in u:
                            cls = "store"
                    break
        rows.append((p.name, n + 1, cur, s.group(3), cls))
by = collections.Counter((r[3], r[4]) for r in rows)
print("total", len(rows), dict(by))
for r in rows:
    if r[4] != "other":
        print("\t".join(map(str, r)))
print("distinct funcs", len(set(r[2] for r in rows)))
