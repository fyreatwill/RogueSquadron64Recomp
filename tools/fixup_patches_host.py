#!/usr/bin/env python3
"""Add declarations N64Recomp cannot emit for external patch callees."""

from pathlib import Path
import sys


DECLARATIONS = (
    "extern void findAndUnlinkSmallestEntry(uint8_t* rdram, "
    "recomp_context* ctx);\n"
)


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {Path(sys.argv[0]).name} GENERATED_PATCHES_C")

    path = Path(sys.argv[1])
    text = path.read_text()
    anchor = '#include "funcs.h"\n'
    if text.count(anchor) != 1:
        raise SystemExit(f"{path}: expected one funcs.h include")
    if "findAndUnlinkSmallestEntry(uint8_t* rdram" in text:
        return 0

    path.write_text(text.replace(anchor, anchor + DECLARATIONS, 1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
