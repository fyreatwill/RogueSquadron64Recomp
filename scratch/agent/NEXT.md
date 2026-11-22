# NEXT (s7810)
HYPOTHESIS-ID: host-override-diff-class
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
s7809 closed the gcc C-patch class (tools/s7809_patch_class_diff.py, sweep row S7809_PATCH_CLASS: 3 live == retail, 6 dead).
Unit: the sibling class = HOST (C/C++) definitions that replace a recompiled game function. s7809 census
(`grep -rhoE 'void X(uint8_t* rdram, recomp_context* ctx)' src` intersected with RecompiledFuncs RECOMP_FUNC names) found 2:
zmemcpy (src/main/upstream_compat.cpp, carries s7490/s7491 hooks) and recomp_entrypoint (boot, not offline-testable -> class c).
Extend s7809 (or a s7810 sibling) to: (1) enumerate this set from the live tree and RED on any unrowed member; (2) differential
the host zmemcpy against the recompiled retail zmemcpy on random (dst, src, len) incl. len 0, unaligned dst/src, overlap both
directions, KSEG0/KSEG1 addresses, and compare r2 + callee-saved regs + full RDRAM; planted mutant (off-by-one len) must read H-differ.
Hypotheses: H-equal (host == retail on every class), H-differ (an overlap/unaligned/len-0 path diverges), H-hollow (generator misses
a branch -> per-branch coverage counters >0 required). If zmemcpy needs host runtime state not linkable offline, say exactly what
and fall back to a [patch-live]-style in-game shadow compare of a sample of calls.
