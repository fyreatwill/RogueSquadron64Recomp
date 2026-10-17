# Session 5312 generated-symbol audit

Candidate: `spawnNpcFormationWithRandomOrientation = 0x800409A4`.

The bounded helper reported `already-synchronized` and renamed zero references
in zero files. Independent inspection found the companion entry in
`../rogue_squadron64/symbol_files/main_overlay.txt`, the named callable body in
`../N64Recomp/RecompiledFuncs/funcs_9.c`, the declaration in `funcs.h`, the
overlay record in `recomp_overlays.inl`, and a direct generated caller in
`funcs_9.c`. No `func_800409A4` placeholder or conflicting fragment was found.

This selects H1 (already synchronized) and rules out H2 (real generated rename)
and H3 (data or ABI-boundary preservation). No build or soak was warranted for
this classification-only unit.
