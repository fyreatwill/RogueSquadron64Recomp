# Generated-symbol audit — Session 5316

Candidate: `initNpcContextFromTransform = 0x80041B8C`.

The bounded helper reported `renamed 0 references in 0 files` and classified
the candidate as `already-synchronized`. Independent checks found the same
name in `rogue_squadron64/symbol_files/main_overlay.txt`, the callable body in
`RecompiledFuncs/funcs_9.c`, its declaration in `funcs.h`, and its overlay
record in `recomp_overlays.inl`. Named generated callers were present in
`funcs_17.c`, `funcs_28.c`, `funcs_38.c`, and `funcs_39.c`. No
`func_80041B8C` placeholder or conflicting fragment was found.

This selects the already-synchronized hypothesis and rules out a real rename
and a data/ABI-preservation case for this address. No build or soak was needed.
The next bounded candidate is `spawnRandomBurstNpcVariantWrapper = 0x80041CBC`.
