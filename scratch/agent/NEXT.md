# NEXT work unit (s905)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`reset3DAudioLists` (`0x80099C2C`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate every listener/voice-list
or table access, reset store, dependent reader/writer, and ownership basis.
Do not add a guard or change game behavior. Do not run a game
build or animating A/B for this source inventory.

Competing hypotheses:

- H-reset-3d-unclassified: a reset store has a hidden dependent state or
  writer/initialization obligation that cannot be classified from the function
  and sibling writers.
- H-reset-3d-fully-classified: both stores are standalone list-root resets and
  their lifecycle writers and readers have a concrete basis.
- H-reset-3d-shape-mismatch: the two reset globals belong to unrelated audio
  structures; record the exact ownership split and stop.

Discriminating measurement: a complete site table for `reset3DAudioLists`,
including both stores, every reader/writer of `0x80153414` and `0x80153418`,
and the companion symbol/lifecycle basis. Any omitted dependency or unproven
ownership rejects full classification.

Exact commands: use `rg` to enumerate `reset3DAudioLists`, `0x80153414`, and
`0x80153418` in `../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded `sed`
windows and the companion `rogue_squadron64` symbol/decomp files. No game
build or soak is planned.
