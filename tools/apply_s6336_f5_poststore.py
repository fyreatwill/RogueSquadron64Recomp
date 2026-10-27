#!/usr/bin/env python3
"""Add a regeneration-preserved readback immediately after generated stores."""
from pathlib import Path
import re
import sys

MARKER = "/* PATCH: s6336 F5 post-store shadow */"

def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply_s6336_f5_poststore.py <RecompiledFuncs>")
    base = Path(sys.argv[1])
    changed = 0
    parity = re.compile(r"rs64_m5_writer_parity\('([BHDW])',\s*(0x[0-9A-Fa-f]+u),\s*U32\(ADD32\((ctx->r\d+),\s*([^\)]+)\)\)")
    for path in sorted(base.glob("funcs_*.c")):
        text = path.read_text()
        if MARKER in text:
            continue
        out = []
        pending = None
        for line in text.splitlines(True):
            out.append(line)
            m = parity.search(line)
            if m:
                pending = m.groups()
                continue
            if pending and ('MEM_' in line or 'SD(' in line):
                width, pc, reg, off = pending
                indent = line[:len(line) - len(line.lstrip())]
                out.append(f"{indent}{{ extern void rs64_f5_store_shadow_post(char, uint32_t, uint32_t); rs64_f5_store_shadow_post('{width}', {pc}, U32(ADD32({reg}, {off}))); }} {MARKER}\n")
                changed += 1
                pending = None
        new = ''.join(out)
        if new != text:
            path.write_text(new)
    print(f"s6336: patched {changed} generated stores")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
