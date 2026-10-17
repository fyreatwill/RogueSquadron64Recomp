# Generated-symbol audit — Session 5307

Candidate: `destroyNpcContextArrays = 0x8003FDD8`.

The bounded helper reported `already-synchronized` and renamed zero references
in zero files. Independent inspection found the companion map entry in
`../rogue_squadron64/symbol_files/main_overlay.txt`, the named callable body in
`../N64Recomp/RecompiledFuncs/funcs_9.c`, its declaration in `funcs.h`, and the
overlay record in `recomp_overlays.inl`. The generated tree also contains a
named call from `endMissionCleanup`; no `func_8003FDD8` placeholder or
conflicting generated fragment was found.

Conclusion: H1 is selected; H2 and H3 are ruled out. No build or soak was
warranted. The next bounded candidate is
`spawnNpcWithSubtype = 0x8003FE9C`.
