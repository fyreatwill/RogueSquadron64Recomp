#!/usr/bin/env python3
"""Install the phase-gated post-free port/retail join in generated funcs."""
from pathlib import Path
import re

ROOT = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
STORE = re.compile(r"^(\s*)MEM_(W|H|B)\((.*?),\s*(.*?)\)\s*=\s*(.*);\s*$")
COMMENT = re.compile(r"^\s*// 0x([0-9A-Fa-f]+):")
GROUPS = {
    "s4306 postfree join": {
        "8008FBB4", "8008FBEC", "8008FBF0", "8008FBF4", "8008FCF8",
        "8008FD08", "8008FD30", "8008FD34", "8008FDC0", "8008FDCC",
        "8008FE60",
    },
    "s4306b postfree join": {
        "8008FB90", "8008FBCC", "8008FD70", "8008FDA8", "8008FDAC", "8008FDB0",
    },
}

def main():
    changed = 0
    for path in sorted(ROOT.glob("funcs_*.c")):
        text = path.read_text()
        lines = text.splitlines()
        out, active, touched = [], None, False
        for line in lines:
            match = COMMENT.match(line)
            if match:
                active = match.group(1).upper()
            out.append(line)
            group = next((name for name, pcs in GROUPS.items() if active in pcs), None)
            if not group or f"PATCH: {group}" in text or not line.lstrip().startswith("MEM_W("):
                continue
            store = STORE.match(line)
            if not store:
                continue
            indent, _, offset, reg, rhs = store.groups()
            addr = f"U32(ADD32({reg}, {offset}))"
            out.append(f"{indent}rs64_s4306_postfree_store(rdram, 0x{active}u, {addr}, U32({rhs})); /* PATCH: {group} */")
            touched = True
            active = None
        if touched:
            result = "\n".join(out) + "\n"
            result = result.replace('#include "funcs.h"\n', '#include "funcs.h"\nextern void rs64_s4306_postfree_store(uint8_t*, uint32_t, uint32_t, uint32_t);\n', 1)
            path.write_text(result)
            changed += 1
    print(f"patched files: {changed}")

if __name__ == "__main__":
    main()
