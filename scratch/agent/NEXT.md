# NEXT (s7489)
HYPOTHESIS-ID: m3-store-path-coverage

s7488 closed EM on L4/L15 (swl/swr: 0 freed-block / slack stores over 63.3M execs, ust-ctl DETECTED in flight both). Levels soak
s7488_ustwatch_levels (L1 dd8 21:9, L7/L10/L12 dd4) is queued: fold its verdict first (score=0 -> EM closed for 6 levels; any
ust_F/ust_Urec/ust_slack -> chase the `[s7488] ust-hit` / `ust-slack` row: pc, fn, blk, loc).

Work unit (class EN): the remaining guest write paths that bypass rs64_s7475_store. Offline census first (no game run needed to start):
1. Enumerate every store form in RecompiledFuncs and say which hook reaches rs64_s7475_store: sw/sh/sb/sd (s5798 STORE_DIAG), swc1/sdc1
   (FPU stores), swl/swr (s7488), sc/scd, cache ops, and stores emitted inside PATCH lines / host helpers that write rdram directly
   (MEM_W/MEM_H/MEM_B macros in src/, rs_memset/rs_memcpy host replacements, osPiStartDma / DMA-to-RDRAM host paths). Script:
   tools/s7489_store_path_census.py -> table (form, sites, hooked y/n, hook name).
2. For each unhooked form with live sites, wrap it like s7488 (same bitmap test -> rs64_s7475_store) in ONE fixup and one build; run
   tools/s7488_ustwatch_recipe.zsh extended with the new counters, LV="4:4 15:8" HOLD=220, plus a form-specific live-block control.
Hypotheses: H-paths-covered (every write form already reaches the canary/UAF watch: close the store side of M3) / H-fpu-gap (swc1/sdc1
unhooked, then measure them) / H-host-gap (host-side rdram writers outside s7486's read set: PI DMA, rs_memcpy replacements).
If the census shows everything hooked, the M3 heap-audit series is done: take the next ladder rung per ITERATION.md 3c.
