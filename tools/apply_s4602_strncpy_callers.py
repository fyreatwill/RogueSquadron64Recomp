#!/usr/bin/env python3
"""Add a phase-scoped caller table for every generated rs_strncpy call."""
from pathlib import Path

ROOT = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s4602 rs_strncpy caller table"

CALLS = {
    "0x80002640", "0x80003AEC", "0x80003B84", "0x8005512C",
    "0x80055590", "0x800555A8", "0x8001FAA8", "0x80022B44",
}

HOOK = (
    '        { extern void rs64_s4602_strncpy_caller(uint8_t*, uint32_t, uint32_t, uint32_t, uint32_t); '
    'rs64_s4602_strncpy_caller(rdram, %s, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6)); } '
    '/* %s */\n'
)

files = {p: p.read_text(encoding="utf-8") for p in ROOT.glob("funcs_*.c")}
if any(MARK in text for text in files.values()):
    for path, text in files.items():
        lines = text.splitlines(keepends=True)
        out = []
        for line in lines:
            if MARK in line:
                import re
                match = re.search(r'rs64_s4602_strncpy_caller\((0x[0-9A-Fa-f]+)u?,', line)
                if not match:
                    raise SystemExit(f"cannot decode existing hook in {path}: {line}")
                out.append(HOOK % (match.group(1) + "u", MARK))
            else:
                out.append(line)
        files[path] = "".join(out)
    for path, text in files.items():
        path.write_text(text, encoding="utf-8")
    print("updated existing caller hooks with RDRAM source access")
    raise SystemExit(0)

patched = 0
for path, text in files.items():
    lines = text.splitlines(keepends=True)
    out = []
    for line in lines:
        out.append(line)
        pc = next((x for x in CALLS if f"// {x}: jal" in line), None)
        if pc is not None:
            out.append(HOOK % (pc + "u", MARK))
            patched += 1
    files[path] = "".join(out)

if patched != len(CALLS):
    raise SystemExit(f"expected {len(CALLS)} caller sites, found {patched}")

for path, text in files.items():
    if MARK in text:
        path.write_text(text, encoding="utf-8")
print(f"patched caller sites: {patched}")
