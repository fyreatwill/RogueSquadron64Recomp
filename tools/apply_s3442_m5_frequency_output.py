#!/usr/bin/env python3
"""Add the s3442 first post-consumer output witnesses to generated output."""
from pathlib import Path
import re

BASE = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARKER = "PATCH: s3442 frequency output"
targets = {
    0x80001C0C: (0x80001B04, 0x80001C0C),
    0x80001CC8: (0x80001CB8, 0x80001CC8),
}
decl = ('extern void rs64_m5_frequency_output_use(uint8_t* rdram, '
        'recomp_context* ctx, uint32_t callsite, uint32_t output_pc);\n')
total = 0

for path in sorted(BASE.glob("funcs_*.c")):
    text = path.read_text()
    lines = text.splitlines(keepends=True)
    out = []
    inserted = 0
    pending = None
    for line in lines:
        match = re.match(r"\s*// 0x([0-9A-Fa-f]{8}): (?:lw|lhu)\s+", line)
        if match:
            pc = int(match.group(1), 16)
            pending = targets.get(pc)
        out.append(line)
        if pending is not None and "ctx->r3 =" in line:
            callsite, output_pc = pending
            if MARKER not in text:
                out.append(
                    f"    rs64_m5_frequency_output_use(rdram, ctx, "
                    f"0x{callsite:08X}u, 0x{output_pc:08X}u); /* {MARKER} */\n"
                )
                inserted += 1
            pending = None
    updated = "".join(out)
    if MARKER in updated and decl not in updated:
        anchor = '#include "funcs.h"\n'
        if updated.count(anchor) != 1:
            raise SystemExit(f"{path}: funcs.h anchor count {updated.count(anchor)}")
        updated = updated.replace(anchor, anchor + decl, 1)
    if updated != text:
        path.write_text(updated)
    if inserted:
        total += inserted
        print(f"{path.name}: {inserted}")

print(f"total: {total}")
