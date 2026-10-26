#!/usr/bin/env python3
"""Add declarations N64Recomp cannot emit for external patch callees."""

from pathlib import Path
import sys


DECLARATIONS = (
    "extern void findAndUnlinkSmallestEntry(uint8_t* rdram, "
    "recomp_context* ctx);\n"
    "extern char* getenv(const char*);\n"
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
    # s6277: shadow-check the C setRngSeed patch (arg passing + guest store) on every call.
    # ROGUESQ_RAND_CTL=1 corrupts the expectation (positive control: mismatches must fire).
    rhead = "RECOMP_FUNC void setRngSeed(uint8_t* rdram, recomp_context* ctx) {\n"
    if text.count(rhead) == 1:
        wrap = (
            "static void rs64_seed_body(uint8_t* rdram, recomp_context* ctx);\n"
            + rhead +
            "    static unsigned n, bad; static int ctl = -1;\n"
            "    if (ctl < 0) ctl = getenv(\"ROGUESQ_RAND_CTL\") != NULL;\n"
            "    int64_t b = (int32_t)0x80000000;\n"
            "    uint32_t want = (uint32_t)ctx->r4 ^ (ctl ? 1u : 0u);\n"
            "    rs64_seed_body(rdram, ctx);\n"
            "    uint32_t got = (uint32_t)MEM_W(0X3470, b);\n"
            "    n++; if (got != want) bad++;\n"
            "    if (n <= 16)\n"
            "        fprintf(stderr, \"[patch-live] setRngSeed call=%u seed=0x%08X stored=0x%08X mismatches=%u ctl=%d\\n\", n, (uint32_t)ctx->r4, got, bad, ctl);\n"
            "}\n"
            "static void rs64_seed_body(uint8_t* rdram, recomp_context* ctx) {\n")
        text = text.replace(rhead, wrap, 1)
    # s6269: PatchesLib is -force_load'ed on macOS, so a stale override would beat the
    # hand-fixed game allocateDisplayListBuffer (funcs_3.c); rename it out of the way.
    stale = "RECOMP_FUNC void allocateDisplayListBuffer("
    if text.count(stale) == 1:
        text = text.replace(stale, "RECOMP_FUNC void unused_patch_allocateDisplayListBuffer(", 1)
    path.write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
