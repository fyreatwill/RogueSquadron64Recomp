#!/usr/bin/env python3
"""Pass the real source register to the s6334 VTX writer witness."""
from pathlib import Path
import sys

MARKER = "/* PATCH: s6334 VTX writer value */"

def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply_s6334_vtx_writer_value.py <RecompiledFuncs>")
    base = Path(sys.argv[1])
    changed = 0
    for path in sorted(base.glob("funcs_*.c")):
        text = path.read_text()
        if MARKER in text:
            continue
        needle = "rs64_m5_writer_parity('W', 0x8000D114u, U32(ADD32(ctx->r2, 0X0)), 0u); /* PATCH: s2190 m5 scalar */"
        if needle not in text:
            continue
        replacement = "rs64_m5_writer_parity('W', 0x8000D114u, U32(ADD32(ctx->r2, 0X0)), U32(ctx->r19)); /* PATCH: s2190 m5 scalar */ " + MARKER
        text = text.replace(needle, replacement, 1)
        path.write_text(text)
        changed += 1
    print(f"s6334: patched {changed} generated files")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
