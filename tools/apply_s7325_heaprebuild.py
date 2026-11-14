#!/usr/bin/env python3
"""s7325 audio-heapgap-read: hook buildHeapFreeList (0x80001F8C) entry.

The retail scene-change heap reset never calls rs_free: waitForPrevFrameDone (0x8000A86C, misnamed) calls 0x80001880 (misnamed
clearFrameReadyFlag), which zeroes the main heap head 0x8010FEFC; the next rs_malloc runs ensureHeapInitialized, which rebuilds the
arena with buildHeapFreeList(head, 0, 0, lo, hi = sp+0x10). clearSceneBssRegion does the same for the overlay-BSS arena (head
0x8010FF00) via queueDeferredClearRequest. Every block in [lo, hi) dies there, so host-side allocation maps (s7317 ALLOCMAP, s6063
HEAPLOG) kept them forever. This inserts at function entry (before the prologue moves sp):
    rs64_s7325_heaprebuild(U32(ctx->r4), U32(ctx->r7), MEM_W(0x10, ctx->r29));
src/main/upstream_compat.cpp drops the dead entries and, under ROGUESQ_S7317_ALLOCMAP, logs one [s7325] line per rebuild with the
spill-arena live blocks/bytes at that moment. Usage: apply_s7325_heaprebuild.py [RecompiledFuncs dir]"""
import sys, pathlib
D = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TAG = "PATCH: s7325 heaprebuild"
f = D / "funcs_0.c"
t = f.read_text(errors="surrogateescape")
if TAG in t:
    print("heaprebuild already applied")
A = ("RECOMP_FUNC void buildHeapFreeList(uint8_t* rdram, recomp_context* ctx) {\n"
     "    uint64_t hi = 0, lo = 0, result = 0;\n    int c1cs = 0;\n")
if TAG not in t:
  assert t.count(A) == 1, "buildHeapFreeList anchor"
  t = t.replace(A, A + "    { extern void rs64_s7325_heaprebuild(uint32_t, uint32_t, uint32_t); rs64_s7325_heaprebuild(U32(ctx->r4), U32(ctx->r7), U32(MEM_W(0x10, ctx->r29))); } /* " + TAG + " */\n", 1)
  f.write_text(t, errors="surrogateescape")
  print("applied heaprebuild")

# Part 2: wrap coalesceFreeHeapBlocks (0x800022F8, misnamed: the scene-change bulk free). It walks the persistent heap (head
# 0x8010FF18) and marks free every allocated block whose header tag lacks 0x80, with no rs_free. The wrapper calls
# rs64_s7325_heapsync() after it, which re-syncs the host maps with the guest heap walk.
TAG2 = "PATCH: s7325 heapsync"
t = f.read_text(errors="surrogateescape")
if TAG2 not in t:
    B = "RECOMP_FUNC void coalesceFreeHeapBlocks(uint8_t* rdram, recomp_context* ctx) {\n"
    assert t.count(B) == 1, "coalesceFreeHeapBlocks anchor"
    W = ("RECOMP_FUNC void coalesceFreeHeapBlocks_s7325_inner(uint8_t* rdram, recomp_context* ctx);\n"
         "RECOMP_FUNC void coalesceFreeHeapBlocks(uint8_t* rdram, recomp_context* ctx) { extern void rs64_s7325_heapsync(uint32_t); "
         "uint32_t _a0 = U32(ctx->r4); coalesceFreeHeapBlocks_s7325_inner(rdram, ctx); rs64_s7325_heapsync(_a0); } /* " + TAG2 + " */\n")
    t = t.replace(B, W + "RECOMP_FUNC void coalesceFreeHeapBlocks_s7325_inner(uint8_t* rdram, recomp_context* ctx) {\n", 1)
    f.write_text(t, errors="surrogateescape")
    print("applied heapsync wrapper")
