#!/usr/bin/env python3
"""Land s3270 alignment + cyclic-walk cap on the live generated free-list walks.

ORIGIN: allocateDisplayListBuffer (func_80007D74) and allocDLBlockToFillRectList
consume guest free-list pointers published by the allocator / findAndUnlink.
Those values were not independently proven legitimate, so this is a safety
guard, not an explanation of the VI-640 or audio route.

patches/heap_guards.c already has the same predicate, but this checkout has
no PatchesLib target. These edits go into the generated host C that actually
links.
"""
from pathlib import Path

GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c")
MARK = "PATCH: s3285 freelist align+cycle"


def apply_text(text: str):
    if MARK in text:
        return text, "already present"

    replacements = [
        (
            "RECOMP_FUNC void allocateDisplayListBuffer(uint8_t* rdram, recomp_context* ctx) {\n"
            "    uint64_t hi = 0, lo = 0, result = 0;\n"
            "    int c1cs = 0;\n",
            "RECOMP_FUNC void allocateDisplayListBuffer(uint8_t* rdram, recomp_context* ctx) {\n"
            "    uint64_t hi = 0, lo = 0, result = 0;\n"
            "    int c1cs = 0;\n"
            "    unsigned s3285_walk = 0; /* PATCH: s3285 freelist align+cycle */\n",
        ),
        (
            "RECOMP_FUNC void allocDLBlockToFillRectList(uint8_t* rdram, recomp_context* ctx) {\n"
            "    uint64_t hi = 0, lo = 0, result = 0;\n"
            "    int c1cs = 0;\n",
            "RECOMP_FUNC void allocDLBlockToFillRectList(uint8_t* rdram, recomp_context* ctx) {\n"
            "    uint64_t hi = 0, lo = 0, result = 0;\n"
            "    int c1cs = 0;\n"
            "    unsigned s3285_walk = 0; /* PATCH: s3285 freelist align+cycle */\n",
        ),
        (
            "        uint32_t r3_lo = U32(ctx->r3);\n"
            "        if (r3_lo < 0x80000000u || r3_lo >= 0x80800000u) {\n"
            "            if (s_alloc_tail_guard2_enabled) {\n"
            "                static int s_alloc_tail_guard2_n = 0;\n"
            "                fprintf(stderr, \"[alloc-tail-guard2] n=%d site=0x80007D9C bad_r3=0x%08X ra=0x%08X\\n\", s_alloc_tail_guard2_n, r3_lo, U32(ctx->r31));\n",
            "        uint32_t r3_lo = U32(ctx->r3);\n"
            "        s3285_walk = 0;\n"
            "        if (r3_lo < 0x80000000u || r3_lo >= 0x80800000u || (r3_lo & 3u) != 0u) {\n"
            "            if (s_alloc_tail_guard2_enabled) {\n"
            "                static int s_alloc_tail_guard2_n = 0;\n"
            "                fprintf(stderr, \"[alloc-tail-guard2] n=%d site=0x80007D9C bad_r3=0x%08X ra=0x%08X\\n\", s_alloc_tail_guard2_n, r3_lo, U32(ctx->r31));\n",
        ),
        (
            "        uint32_t r4_lo = U32(ctx->r4);\n"
            "        if (r4_lo < 0x80000000u || r4_lo >= 0x80800000u) {\n"
            "            if (s_alloc_tail_guard3_enabled) {\n"
            "                static int s_alloc_tail_guard3_n = 0;\n"
            "                fprintf(stderr, \"[alloc-tail-guard3] n=%d site=0x80007DA8 bad_r4=0x%08X ra=0x%08X\\n\", s_alloc_tail_guard3_n, r4_lo, U32(ctx->r31));\n",
            "        uint32_t r4_lo = U32(ctx->r4);\n"
            "        if (r4_lo < 0x80000000u || r4_lo >= 0x80800000u || (r4_lo & 3u) != 0u || ++s3285_walk >= 0x8000u) {\n"
            "            if (s_alloc_tail_guard3_enabled) {\n"
            "                static int s_alloc_tail_guard3_n = 0;\n"
            "                fprintf(stderr, \"[alloc-tail-guard3] n=%d site=0x80007DA8 bad_r4=0x%08X ra=0x%08X\\n\", s_alloc_tail_guard3_n, r4_lo, U32(ctx->r31));\n",
        ),
        (
            "        if (r4_lo < 0x80000000u || r4_lo >= 0x80800000u || r4_hi != 0xFFFFFFFFu) {\n"
            "            if (s_alloc_tail_guard4_enabled) {\n"
            "                static int s_alloc_tail_guard4_n = 0;\n"
            "                fprintf(stderr, \"[alloc-tail-guard4] n=%d site=0x80007DAC bad_r4=0x%08X hi=0x%08X ra=0x%08X\\n\", s_alloc_tail_guard4_n, r4_lo, r4_hi, U32(ctx->r31));\n",
            "        if (r4_lo < 0x80000000u || r4_lo >= 0x80800000u || (r4_lo & 3u) != 0u || r4_hi != 0xFFFFFFFFu) {\n"
            "            if (s_alloc_tail_guard4_enabled) {\n"
            "                static int s_alloc_tail_guard4_n = 0;\n"
            "                fprintf(stderr, \"[alloc-tail-guard4] n=%d site=0x80007DAC bad_r4=0x%08X hi=0x%08X ra=0x%08X\\n\", s_alloc_tail_guard4_n, r4_lo, r4_hi, U32(ctx->r31));\n",
        ),
        (
            "    // 0x80007E20: lw          $v1, 0x0($v0)\n"
            "    ctx->r3 = MEM_W(ctx->r2, 0X0);\n"
            "    // 0x80007E24: sw          $a0, 0x0($v1)\n",
            "    // 0x80007E20: lw          $v1, 0x0($v0)\n"
            "    { // PATCH: s3285 freelist align+cycle tail\n"
            "        uint32_t s3285_tail = U32(ctx->r2);\n"
            "        if (s3285_tail < 0x80000000u || s3285_tail >= 0x80800000u || (s3285_tail & 3u) != 0u) {\n"
            "            ctx->r2 = 0;\n"
            "            ctx->r31 = MEM_W(ctx->r29, 0X10);\n"
            "            ctx->r29 = ADD32(ctx->r29, 0X18);\n"
            "            return;\n"
            "        }\n"
            "        ctx->r3 = MEM_W(ctx->r2, 0X0);\n"
            "        s3285_tail = U32(ctx->r3);\n"
            "        if (s3285_tail < 0x80000000u || s3285_tail >= 0x80800000u || (s3285_tail & 3u) != 0u) {\n"
            "            ctx->r2 = 0;\n"
            "            ctx->r31 = MEM_W(ctx->r29, 0X10);\n"
            "            ctx->r29 = ADD32(ctx->r29, 0X18);\n"
            "            return;\n"
            "        }\n"
            "    }\n"
            "    // 0x80007E24: sw          $a0, 0x0($v1)\n",
        ),
        (
            "        uint32_t r5_lo = U32(ctx->r5);\n"
            "        if (r5_lo < 0x80000000u || r5_lo >= 0x80800000u) {\n"
            "            if (s_alloc_tail_guard2_enabled) {\n"
            "                static int s_alloc_tail_guard2_n = 0;\n"
            "                fprintf(stderr, \"[alloc-tail-guard2] n=%d site=0x80007E84 bad_r5=0x%08X ra=0x%08X\\n\", s_alloc_tail_guard2_n, r5_lo, U32(ctx->r31));\n",
            "        uint32_t r5_lo = U32(ctx->r5);\n"
            "        s3285_walk = 0;\n"
            "        if (r5_lo < 0x80000000u || r5_lo >= 0x80800000u || (r5_lo & 3u) != 0u) {\n"
            "            if (s_alloc_tail_guard2_enabled) {\n"
            "                static int s_alloc_tail_guard2_n = 0;\n"
            "                fprintf(stderr, \"[alloc-tail-guard2] n=%d site=0x80007E84 bad_r5=0x%08X ra=0x%08X\\n\", s_alloc_tail_guard2_n, r5_lo, U32(ctx->r31));\n",
        ),
        (
            "        uint32_t r3_lo = U32(ctx->r3);\n"
            "        if (r3_lo < 0x80000000u || r3_lo >= 0x80800000u) {\n"
            "            if (s_alloc_tail_guard3_enabled) {\n"
            "                static int s_alloc_tail_guard3_n = 0;\n"
            "                fprintf(stderr, \"[alloc-tail-guard3] n=%d site=0x80007E90 bad_r3=0x%08X ra=0x%08X\\n\", s_alloc_tail_guard3_n, r3_lo, U32(ctx->r31));\n",
            "        uint32_t r3_lo = U32(ctx->r3);\n"
            "        if (r3_lo < 0x80000000u || r3_lo >= 0x80800000u || (r3_lo & 3u) != 0u || ++s3285_walk >= 0x8000u) {\n"
            "            if (s_alloc_tail_guard3_enabled) {\n"
            "                static int s_alloc_tail_guard3_n = 0;\n"
            "                fprintf(stderr, \"[alloc-tail-guard3] n=%d site=0x80007E90 bad_r3=0x%08X ra=0x%08X\\n\", s_alloc_tail_guard3_n, r3_lo, U32(ctx->r31));\n",
        ),
        (
            "        if (r3_lo < 0x80000000u || r3_lo >= 0x80800000u || r3_hi != 0xFFFFFFFFu) {\n"
            "            if (s_alloc_tail_guard4_enabled) {\n"
            "                static int s_alloc_tail_guard4_n = 0;\n"
            "                fprintf(stderr, \"[alloc-tail-guard4] n=%d site=0x80007E94 bad_r3=0x%08X hi=0x%08X ra=0x%08X\\n\", s_alloc_tail_guard4_n, r3_lo, r3_hi, U32(ctx->r31));\n",
            "        if (r3_lo < 0x80000000u || r3_lo >= 0x80800000u || (r3_lo & 3u) != 0u || r3_hi != 0xFFFFFFFFu) {\n"
            "            if (s_alloc_tail_guard4_enabled) {\n"
            "                static int s_alloc_tail_guard4_n = 0;\n"
            "                fprintf(stderr, \"[alloc-tail-guard4] n=%d site=0x80007E94 bad_r3=0x%08X hi=0x%08X ra=0x%08X\\n\", s_alloc_tail_guard4_n, r3_lo, r3_hi, U32(ctx->r31));\n",
        ),
    ]

    n = 0
    for old, new in replacements:
        c = text.count(old)
        if c != 1:
            raise SystemExit(f"s3285 anchor count={c} for {old[:80]!r}")
        text = text.replace(old, new, 1)
        n += 1
    return text, f"applied {n} anchors"


def main():
    text = GEN.read_text()
    text, msg = apply_text(text)
    if msg == "already present":
        print(f"{GEN}: s3285 already present")
        return
    GEN.write_text(text)
    print(f"{GEN}: s3285 {msg}")


if __name__ == "__main__":
    main()
