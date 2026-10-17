# Session 5313 generated-symbol audit

Candidate: `computeNpcGroupCentroidAndCull = 0x8004118C`.

The bounded helper reported `already-synchronized` and renamed zero references
in zero files. Independent inspection found the companion entry in
`../rogue_squadron64/symbol_files/main_overlay.txt`, the named callable body in
`../N64Recomp/RecompiledFuncs/funcs_9.c`, the declaration in `funcs.h`, the
overlay record in `recomp_overlays.inl`, and two direct generated callers in
`funcs_9.c`. No `func_8004118C` placeholder or conflicting fragment was found.

This selects H1 (already synchronized) and rules out H2 (real generated rename)
and H3 (data or ABI-boundary preservation). No build or soak was warranted for
this classification-only unit.
