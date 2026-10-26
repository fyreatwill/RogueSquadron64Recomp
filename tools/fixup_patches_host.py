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

    text = text.replace(anchor, anchor + "#include <stdio.h>\n" + DECLARATIONS, 1)
    # s6269 positive control: proves the PatchesLib isCinematicActive is the live one.
    head = "RECOMP_FUNC void isCinematicActive(uint8_t* rdram, recomp_context* ctx) {\n"
    probe = ('    { static unsigned n; n++; if ((n & (n - 1u)) == 0) '
             'fprintf(stderr, "[patch-live] isCinematicActive calls=%u\\n", n); }\n')
    if text.count(head) == 1:
        text = text.replace(head, head + probe, 1)
    # s6269: PatchesLib is -force_load'ed on macOS, so a stale override would beat the
    # hand-fixed game allocateDisplayListBuffer (funcs_3.c); rename it out of the way.
    stale = "RECOMP_FUNC void allocateDisplayListBuffer("
    if text.count(stale) == 1:
        text = text.replace(stale, "RECOMP_FUNC void unused_patch_allocateDisplayListBuffer(", 1)
    path.write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
