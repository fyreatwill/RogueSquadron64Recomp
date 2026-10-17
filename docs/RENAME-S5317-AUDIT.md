# Generated-symbol audit — Session 5317

Candidate: `spawnRandomBurstNpcVariantWrapper = 0x80041CBC`

The bounded helper reported `renamed 0 references in 0 files` and classified
the candidate as `already-synchronized`.

Independent checks found the companion record in
`../rogue_squadron64/symbol_files/main_overlay.txt`, a named callable body in
`../N64Recomp/RecompiledFuncs/funcs_9.c`, the named prototype in `funcs.h`,
and the named overlay entry in `recomp_overlays.inl`. Generated callers also
invoke `spawnRandomBurstNpcVariantWrapper`; no `func_80041CBC` placeholder or
conflicting fragment was found.

The wrapper body passes handler `0x800403EC` (`randomBurstNpcHandlerVariant`),
type `4`, and subtype `15` to `spawnNpcOfType`, matching the companion
description. H1 is selected; H2 and H3 are ruled out for this address.

No build or soak was run because this was a bounded classification-only unit.
