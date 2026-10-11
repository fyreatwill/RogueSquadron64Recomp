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
    '        { extern void rs64_s4602_strncpy_caller(uint32_t, uint32_t, uint32_t, uint32_t); '
    'rs64_s4602_strncpy_caller(%s, U32(ctx->r4), U32(ctx->r5), U32(ctx->r6)); } '
    '/* %s */\n'
)

files = {p: p.read_text(encoding="utf-8") for p in ROOT.glob("funcs_*.c")}
if any(MARK in text for text in files.values()):
    moved = 0
    for path, text in files.items():
        lines = text.splitlines(keepends=True)
        hooks = [line.strip() for line in lines if MARK in line]
        if not hooks:
            continue
        lines = [line for line in lines if MARK not in line]
        out = []
        i = 0
        while i < len(lines):
            out.append(lines[i])
            if "rs_strncpy(rdram, ctx);" in lines[i]:
                if not hooks:
                    raise SystemExit(f"too few hooks in {path}")
                hook = hooks.pop(0)
                out.insert(len(out) - 1, "        " + hook + "\n")
                moved += 1
            i += 1
        if hooks:
            raise SystemExit(f"too many hooks in {path}")
        files[path] = "".join(out)
    for path, text in files.items():
        path.write_text(text, encoding="utf-8")
    print(f"relocated caller hooks after delay slots: {moved}")
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
