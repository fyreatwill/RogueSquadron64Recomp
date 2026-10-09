#!/usr/bin/env python3
"""Add a regeneration-replayable scalar-store census for physical 0x20..0x30."""
from pathlib import Path
import re

BASE = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARKER = "PATCH: s4340 lowfield writer"
STORE = re.compile(
    r"^(\s*)MEM_([BHW])\(([^,]+),\s*([^\)]+)\)\s*=\s*(.+);\s*$"
)
PC = re.compile(r"^\s*// 0x([0-9A-Fa-f]{8}):")

total = 0
files = 0
for path in sorted(BASE.glob("funcs_*.c")):
    text = path.read_text()
    if MARKER in text:
        continue
    lines = text.splitlines(keepends=True)
    out = []
    last_pc = None
    inserted = 0
    for line in lines:
        match_pc = PC.match(line)
        if match_pc:
            last_pc = int(match_pc.group(1), 16)
        out.append(line)
        match = STORE.match(line.rstrip("\n"))
        if not match or last_pc is None:
            continue
        indent, width, offset, reg, value = match.groups()
        out.append(
            f"{indent}rs64_m5_lowfield_store('{width}', 0x{last_pc:08X}u, "
            f"U32(ADD32({reg.strip()}, {offset.strip()})), U32({value.strip()})); "
            f"/* {MARKER} */\n"
        )
        inserted += 1
    if not inserted:
        continue
    anchor = '#include "funcs.h"\n'
    if text.count(anchor) != 1:
        raise SystemExit(f"{path}: funcs.h anchor count {text.count(anchor)}")
    decl = "extern void rs64_m5_lowfield_store(char, uint32_t, uint32_t, uint32_t);\n"
    rewritten = "".join(out).replace(anchor, anchor + decl, 1)
    path.write_text(rewritten)
    total += inserted
    files += 1
    print(f"{path.name}: {inserted}")

print(f"files: {files} stores: {total}")
