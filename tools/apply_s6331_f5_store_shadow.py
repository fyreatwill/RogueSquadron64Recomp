#!/usr/bin/env python3
"""Install the regeneration-preserved s6331 F5 VTX store-shadow call."""
from pathlib import Path
import sys

MARKER = "/* PATCH: s6331 F5 VTX store shadow */"

def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply_s6331_f5_store_shadow.py <RecompiledFuncs>")
    base = Path(sys.argv[1])
    changed = 0
    for path in sorted(base.glob("funcs_*.c")):
        text = path.read_text()
        if MARKER in text:
            continue
        anchor = "    extern void rs64_m5_route_value_writer(char width, uint32_t pc,\n"
        if anchor not in text:
            continue
        needle = "        rs64_m5_route_value_writer(width, pc, addr, value);\n    }\n"
        if needle not in text:
            raise SystemExit(f"{path}: writer helper call anchor missing")
        replacement = (
            "        rs64_m5_route_value_writer(width, pc, addr, value);\n"
            "    }\n"
            "    { extern void rs64_f5_store_shadow(char width, uint32_t pc, "
            "uint32_t addr, uint32_t value);\n"
            "      rs64_f5_store_shadow(width, pc, addr, value); } " + MARKER + "\n"
        )
        text = text.replace(needle, replacement, 1)
        path.write_text(text)
        changed += 1
    print(f"s6331: patched {changed} generated files")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
