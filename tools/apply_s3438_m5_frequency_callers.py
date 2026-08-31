#!/usr/bin/env python3
"""Apply the s3438 caller census to an already-generated recomp tree."""
from pathlib import Path
import re

BASE = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARKER = "PATCH: s3438 frequency caller"
total = 0

for path in sorted(BASE.glob("funcs_*.c")):
    text = path.read_text()
    if MARKER in text or "osRecvMesg_recomp(rdram, ctx);" not in text:
        continue
    lines = text.splitlines(keepends=True)
    out = []
    callsite = None
    inserted = 0
    for line in lines:
        match = re.match(r"\s*// 0x([0-9A-Fa-f]{8}): jal\s+0x800331D0", line)
        if match:
            callsite = int(match.group(1), 16)
        if "osRecvMesg_recomp(rdram, ctx);" in line and callsite is not None:
            out.append(
                f"    rs64_m5_frequency_caller(rdram, ctx, 0x{callsite:08X}u); "
                f"/* {MARKER} */\n"
            )
            inserted += 1
            callsite = None
        out.append(line)
    if not inserted:
        continue
    anchor = '#include "funcs.h"\n'
    if text.count(anchor) != 1:
        raise SystemExit(f"{path}: funcs.h anchor count {text.count(anchor)}")
    decl = (
        'extern void rs64_m5_frequency_caller(uint8_t* rdram, '
        'recomp_context* ctx, uint32_t callsite);\n'
    )
    path.write_text("".join(out).replace(anchor, anchor + decl, 1))
    total += inserted
    print(f"{path.name}: {inserted}")

print(f"total: {total}")
