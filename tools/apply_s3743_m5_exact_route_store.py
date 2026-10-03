#!/usr/bin/env python3
"""Add a focused witness for generated stores using route-object offsets."""

from pathlib import Path
import re

BASE = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s3743 M5 exact route store"
STORE = re.compile(
    r'^(\s*)MEM_([BHW])\(([-+]?0X[0-9A-Fa-f]+),\s*(ctx->r[0-9]+)\)\s*=\s*(.*);\s*$'
)
PC = re.compile(r'^\s*//\s*0x([0-9A-Fa-f]+):')

changed = 0
sites = 0
for path in sorted(BASE.glob("funcs_*.c")):
    text = path.read_text()
    if MARK in text:
        continue
    current_pc = 0
    out = []
    file_sites = 0
    for line in text.splitlines(True):
        match_pc = PC.match(line)
        if match_pc:
            current_pc = int(match_pc.group(1), 16)
        match = STORE.match(line.rstrip("\n"))
        out.append(line)
        if not match or match.group(3).upper() not in {"0X22", "0X60"}:
            continue
        indent, width, offset, reg, value = match.groups()
        out.append(
            f"{indent}{{ /* {MARK} */\n"
            f"{indent}    extern void rs64_m5_exact_route_store(char width, unsigned pc, unsigned addr, unsigned value);\n"
            f"{indent}    rs64_m5_exact_route_store('{width}', 0x{current_pc:08X}u, U32(ADD32({reg}, {offset})), U32({value}));\n"
            f"{indent}}}\n"
        )
        file_sites += 1
    if file_sites:
        path.write_text("".join(out))
        changed += 1
        sites += file_sites

print(f"s3743 exact-route witness: files={changed} sites={sites}")
