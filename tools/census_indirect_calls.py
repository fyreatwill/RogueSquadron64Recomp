#!/usr/bin/env python3
"""M3 idiom census: register-target indirect calls (jalr/jr) in generated code.
Finds LOOKUP_FUNC(ctx->rN) sites, walks back up to 13 lines in the same
function for the last write to rN and classifies its source (mem-load / arith /
const / other / unresolved). Constant LOOKUP_FUNC(0x..) sites are counted
separately (static calls via the manual-patch range). Asserts against a grep."""
from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
FUNC = re.compile(r"\b(\w+)\(uint8_t\*\s*rdram,\s*recomp_context\*\s*ctx\)\s*\{")
SITE = re.compile(r"LOOKUP_FUNC\(ctx->r(\d+)\)")
tot = Counter()
sites = []
grep_reg = grep_const = 0
for p in sorted(ROOT.glob("funcs_*.c")):
    lines = p.read_text(errors="replace").splitlines()
    cur = ""
    for i, l in enumerate(lines):
        m = FUNC.search(l)
        if m:
            cur = m.group(1)
        if l.lstrip().startswith("#"):
            continue
        if "LOOKUP_FUNC(0x" in l:
            grep_const += 1
        m = SITE.search(l)
        if not m:
            continue
        grep_reg += 1
        r = m.group(1)
        kind = "unresolved"
        src = ""
        for j in range(i - 1, max(i - 14, -1), -1):
            if re.match(rf"\s*ctx->r{r} = ", lines[j]):
                src = lines[j].strip()
                if re.search(r"MEM_(W|WU|H|HU|B|BU)\(", src) or "do_l" in src:
                    kind = "mem-load"
                elif "ctx->r" in src.split("=", 1)[1]:
                    kind = "arith"
                elif "0x" in src:
                    kind = "const"
                else:
                    kind = "other"
                break
        tot[kind] += 1
        sites.append((kind, p.name, i + 1, cur, r, src))
print("reg-target sites:", grep_reg, "const-target sites:", grep_const, "classified:", dict(tot))
assert sum(tot.values()) == grep_reg
print("functions:", len({(s[1], s[3]) for s in sites}))
for s in sites:
    if s[0] != "const":
        print(s)
