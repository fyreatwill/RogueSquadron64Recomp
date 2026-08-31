#!/usr/bin/env python3
"""Add the s3441 post-receive consumer witness to generated output."""
from pathlib import Path
import re

BASE = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARKER = "PATCH: s3441 frequency consumer"
targets = {0x80001B04, 0x80001CB8, 0x80006EFC, 0x80006F5C}
total = 0

for path in sorted(BASE.glob("funcs_*.c")):
    text = path.read_text()
    if MARKER in text:
        continue
    lines = text.splitlines(keepends=True)
    out = []
    pending = None
    inserted = 0
    for line in lines:
        match = re.match(r"\s*// 0x([0-9A-Fa-f]{8}): jal\s+0x800331D0", line)
        if match:
            candidate = int(match.group(1), 16)
            pending = candidate if candidate in targets else None
        out.append(line)
        if pending is not None and re.match(r"\s*after_0:", line):
            out.append(
                f"    rs64_m5_frequency_consumer(rdram, ctx, 0x{pending:08X}u); "
                f"/* {MARKER} */\n"
            )
            inserted += 1
            pending = None
    if not inserted:
        continue
    anchor = '#include "funcs.h"\n'
    if text.count(anchor) != 1:
        raise SystemExit(f"{path}: funcs.h anchor count {text.count(anchor)}")
    decl = (
        'extern void rs64_m5_frequency_consumer(uint8_t* rdram, '
        'recomp_context* ctx, uint32_t callsite);\n'
    )
    path.write_text("".join(out).replace(anchor, anchor + decl, 1))
    total += inserted
    print(f"{path.name}: {inserted}")

print(f"total: {total}")
