# NEXT work unit (s904)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`update3DAudioFrame` (`0x800998E8`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate every listener/voice-list
or table access, derived pointer, bound/sentinel/state check, helper call, and
writer basis. Do not add a guard or change game behavior. Do not run a game
build or animating A/B for this source inventory.

Competing hypotheses:

- H-update-3d-unclassified: at least one listener/voice-list access, derived
  pointer, or state value lacks structural or writer/legitimacy support.
- H-update-3d-fully-classified: all accesses are bounded or guarded and every
  dynamic input has a concrete writer/legitimacy basis.
- H-update-3d-shape-mismatch: the function combines unrelated listener,
  voice-chain, spatial-record, and queue shapes; record exact sites and stop.

Discriminating measurement: a complete site table for `update3DAudioFrame`,
including guest address, operation, derived value, bound/state check, helper
argument shape, and the writer that established each input. Any omitted access
or unproven writer rejects full classification.

Exact commands: use `rg` to enumerate `update3DAudioFrame` and its
`MEM_*`/`jal`/`goto` sites in `../N64Recomp/RecompiledFuncs/funcs_26.c`, then
bounded `sed` windows and the companion `rogue_squadron64` symbol/decomp
files. No game build or soak is planned.
