#!/usr/bin/env python3
"""Census of 64-bit LD loads in generated code: GPR destinations (integer ld)
versus FPR destinations (ldc1). Only GPR loads can reconstruct a pointer."""

from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
FILES = sorted(ROOT.glob("funcs_*.c"))
ANY = re.compile(r"\bLD\(")
GPR = re.compile(r"ctx->r(\d+)\s*=\s*LD\(ctx->r(\d+),\s*(-?0[xX][0-9A-Fa-f]+|-?\d+)\s*\)")
FPR = re.compile(r"ctx->f\d+\.u64\s*=\s*LD\(")
FUNCTION = re.compile(r"\b(\w+)\(uint8_t\*\s*rdram,\s*recomp_context\*\s*ctx\)\s*\{")


def main():
    total = gpr = fpr = 0
    rows = []
    for p in FILES:
        cur = ""
        lines = p.read_text(errors="replace").splitlines()
        for n, line in enumerate(lines):
            m = FUNCTION.search(line)
            if m:
                cur = m.group(1)
            if not ANY.search(line):
                continue
            total += 1
            if FPR.search(line):
                fpr += 1
                continue
            m = GPR.search(line)
            if m:
                gpr += 1
                use = " | ".join(x.strip() for x in lines[n + 1:n + 4] if x.strip())
                rows.append((p.name, n + 1, cur, f"r{m.group(2)}", m.group(3), f"r{m.group(1)}", use))
    unclassified = total - gpr - fpr
    print(f"all_ld={total} fpr_dest={fpr} gpr_dest={gpr} unclassified={unclassified}")
    assert unclassified == 0, "LD sites matched neither FPR nor GPR form"
    for r in rows:
        print("\t".join(map(str, r)))


if __name__ == "__main__":
    main()
