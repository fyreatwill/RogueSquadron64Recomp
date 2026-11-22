#!/usr/bin/env python3
"""Add a regeneration-preserved readback immediately after generated stores."""
from pathlib import Path
import re
import sys

MARKER = "/* PATCH: s6336 F5 post-store shadow */"

PCC = re.compile(r"^\s*// 0x([0-9A-Fa-f]{8}):")


def is_store(line):
    # s7787: s4984 rewrites the voice base/count stores (0x8008F0EC/0x8008F0CC) to __atomic_store_n, which the old
    # MEM_/SD( test missed: F0EC's pending was overwritten (no shadow) and F0CC's shadow latched onto the lhu at 0x8008F0DC.
    return 'MEM_' in line or 'SD(' in line or '__atomic_store_n(' in line


def repair(path, text, parity):
    """s7787 repair for trees patched before the fix: drop shadow lines that sit under another pc, add the missing ones
    right after their store line. Idempotent (a correct tree is left unchanged)."""
    lines = text.splitlines(True)
    shadow = re.compile(r"rs64_f5_store_shadow_post\('[BHDW]', 0x([0-9A-Fa-f]{8})u")
    out, pc, moved = [], None, 0
    for line in lines:
        m = PCC.match(line)
        if m:
            pc = int(m.group(1), 16)
        sm = shadow.search(line) if MARKER in line else None
        if sm and int(sm.group(1), 16) != pc:
            moved += 1
            continue
        out.append(line)
    have = {int(x, 16) for x in shadow.findall("".join(out))}
    res, pending = [], None
    for line in out:
        res.append(line)
        m = parity.search(line)
        if m and int(m.group(2)[:-1], 16) not in have:
            pending = m.groups(); continue
        if pending and PCC.match(line):
            pending = None
        if pending and is_store(line):
            width, pcs, reg, off = pending
            indent = line[:len(line) - len(line.lstrip())]
            res.append(f"{indent}{{ extern void rs64_f5_store_shadow_post(char, uint32_t, uint32_t); rs64_f5_store_shadow_post('{width}', {pcs}, U32(ADD32({reg}, {off}))); }} {MARKER}\n")
            have.add(int(pcs[:-1], 16)); pending = None; moved += 1
    new = "".join(res)
    if new != text:
        path.write_text(new)
    return moved


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply_s6336_f5_poststore.py <RecompiledFuncs>")
    base = Path(sys.argv[1])
    changed = 0
    parity = re.compile(r"rs64_m5_writer_parity\('([BHDW])',\s*(0x[0-9A-Fa-f]+u),\s*U32\(ADD32\((ctx->r\d+),\s*([^\)]+)\)\)")
    for path in sorted(base.glob("funcs_*.c")):
        text = path.read_text()
        if MARKER in text:
            n = repair(path, text, parity)
            changed += n
            continue
        out = []
        pending = None
        for line in text.splitlines(True):
            out.append(line)
            m = parity.search(line)
            if m:
                pending = m.groups()
                continue
            if pending and PCC.match(line):
                pending = None   # s7787: the store line never came under its own pc; never latch onto a later instruction
            if pending and is_store(line):
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
