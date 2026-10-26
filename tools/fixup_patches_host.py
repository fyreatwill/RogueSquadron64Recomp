#!/usr/bin/env python3
"""Add declarations N64Recomp cannot emit for external patch callees."""

from pathlib import Path
import sys


DECLARATIONS = (
    "extern void findAndUnlinkSmallestEntry(uint8_t* rdram, "
    "recomp_context* ctx);\n"
    "extern char* getenv(const char*);\n"
    "extern void findAndUnlinkSmallestEntry_s6088_inner(uint8_t* rdram, "
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
    if "extern char* getenv(const char*);" in text:
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
    # s6278: findAndUnlinkSmallestEntry C patch (multi-call, stateful). Invariant per call:
    # a non-NULL return leaves the entry at the head of the list at [0x80128EF8] with
    # prev==0. ROGUESQ_FIND_CTL=1 corrupts the expectation (control: bad must fire).
    # NULL returns (dd>=3 exhaustion signature) dump the pool state once (first 3).
    fhead = "RECOMP_FUNC void findAndUnlinkSmallestEntry(uint8_t* rdram, recomp_context* ctx) {\n"
    if text.count(fhead) == 1:
        wrap = (
            "static void rs64_find_body(uint8_t* rdram, recomp_context* ctx);\n"
            + fhead +
            "    static unsigned n, nulls, bad, dumps; static int ctl = -1;\n"
            "    if (ctl < 0) ctl = getenv(\"ROGUESQ_FIND_CTL\") != NULL;\n"
            "    int64_t b = (int32_t)0x80120000;\n"  # s6280: was 0x80000000 -> read code at 0x80008EF8 (not 0x80128EF8) as the list head
            "    static int off = -1; if (off < 0) off = getenv(\"ROGUESQ_FIND_OFF\") != NULL;\n"
            "    if (off) findAndUnlinkSmallestEntry_s6088_inner(rdram, ctx); else rs64_find_body(rdram, ctx);\n"
            "    n++;\n"
            "    uint32_t head = (uint32_t)MEM_W(0X8EF8, b);\n"
            "    if (ctx->r2 == 0) {\n"
            "        nulls++;\n"
            "        if (dumps < 3) {\n"
            "            dumps++;\n"
            "            uint32_t cnt = MEM_HU(0X8EF0, b), bk = (uint32_t)MEM_W(0X8F00, b);\n"
            "            fprintf(stderr, \"[find-null] call=%u nulls=%u buckets=%u arr=0x%08X usedhead=0x%08X\\n\", n, nulls, cnt, bk, head);\n"
            "            for (uint32_t i = 0; i < cnt && i < 64; i++) {\n"
            "                uint32_t e = (uint32_t)MEM_W(i * 4, (int64_t)(int32_t)bk); unsigned len = 0, z = 0;\n"
            "                while (e && len < 100000) { len++; if (!MEM_HU(8, (int64_t)(int32_t)e)) z++; e = (uint32_t)MEM_W(0, (int64_t)(int32_t)e); }\n"
            "                fprintf(stderr, \"[find-null]  bucket %u len=%u zero_size=%u\\n\", i, len, z);\n"
            "            }\n"
            "        }\n"
            "    } else {\n"
            "        uint32_t prev = head ? (uint32_t)MEM_W(4, (int64_t)(int32_t)head) : 1u;\n"
            "        if (head == 0 || prev != (ctl ? 1u : 0u)) bad++;\n"
            "    }\n"
            "    if (n == 1 || (n & (n - 1u)) == 0)\n"
            "        fprintf(stderr, \"[patch-live] findAndUnlinkSmallestEntry calls=%u nulls=%u bad=%u ctl=%d\\n\", n, nulls, bad, ctl);\n"
            "}\n"
            "static void rs64_find_body(uint8_t* rdram, recomp_context* ctx) {\n")
        text = text.replace(fhead, wrap, 1)
    # s6269: PatchesLib is -force_load'ed on macOS, so a stale override would beat the
    # hand-fixed game allocateDisplayListBuffer (funcs_3.c); rename it out of the way.
    stale = "RECOMP_FUNC void allocateDisplayListBuffer("
    if text.count(stale) == 1:
        text = text.replace(stale, "RECOMP_FUNC void unused_patch_allocateDisplayListBuffer(", 1)
    path.write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
