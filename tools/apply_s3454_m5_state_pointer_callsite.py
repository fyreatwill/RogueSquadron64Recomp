#!/usr/bin/env python3
"""Install the regeneration-safe pre-rs_free M5 producer witness."""
from pathlib import Path
import re

BASE = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARKER = "PATCH: s3454 state-pointer callsite"
DECL = ('extern void rs64_m5_state_pointer_callsite(recomp_context* ctx, '
        'uint32_t call_pc);\n')

for path in sorted(BASE.glob("funcs_*.c")):
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        text = re.sub(
            r"(\n)(    )rs_free\(rdram, ctx\);\n"
            r"    rs64_m5_state_pointer_callsite\(ctx, (0x[0-9A-F]+u)\);"
            r" /\* " + re.escape(MARKER) + r" \*/\n",
            r"\1\2rs64_m5_state_pointer_callsite(ctx, \3); /* " + MARKER + r" */\n"
            r"\2rs_free(rdram, ctx);\n",
            text,
        )
        path.write_text(text, encoding="utf-8")
        print(f"{path.name}: reordered")
        continue
    lines = text.splitlines(keepends=True)
    out = []
    pending = None
    inserted = 0
    for line in lines:
        match = re.search(r"// 0x([0-9A-Fa-f]{8}): jal +0x80001C98", line)
        if match:
            pending = int(match.group(1), 16)
        if pending is not None and line.strip() == "rs_free(rdram, ctx);":
            out.append(f"    rs64_m5_state_pointer_callsite(ctx, 0x{pending:08X}u); /* {MARKER} */\n")
            pending = None
            inserted += 1
        out.append(line)
    if not inserted:
        continue
    updated = "".join(out)
    anchor = '#include "funcs.h"\n'
    if updated.count(anchor) != 1:
        raise SystemExit(f"{path}: funcs.h anchor count mismatch")
    updated = updated.replace(anchor, anchor + DECL, 1)
    path.write_text(updated, encoding="utf-8")
    print(f"{path.name}: {inserted}")
