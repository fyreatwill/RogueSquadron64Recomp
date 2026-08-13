# NEXT work unit (s903)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`dispatchPrioritizedSoundQueue` (`0x80099720`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate every queue/group table
access, node dereference, bound/sentinel/state check, helper call, and writer
basis. Do not add a guard or change game behavior. Do not run a game build or
animating A/B for this source inventory.

Competing hypotheses:

- H-dispatch-priority-unclassified: at least one queue/table access, derived
  pointer, or state value lacks a structural or writer/legitimacy basis.
- H-dispatch-priority-fully-classified: all accesses and transformations are
  bounded, and every dynamic input has a concrete writer/legitimacy basis.
- H-dispatch-priority-shape-mismatch: the dispatcher combines unrelated queue,
  voice-record, and helper/state shapes; record exact sites and stop rather
  than mixing them.

Discriminating measurement: a complete site table for
`dispatchPrioritizedSoundQueue`, including guest address, operation, derived
value, bound/state check, helper argument shape, and the writer that
established each input. Any omitted access or unproven writer rejects full
classification.

Exact commands: use `rg` to enumerate the function's `MEM_*`, `jal`, and
`goto` sites in `../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded `sed`
windows and the companion `rogue_squadron64` symbol/decomp files. No game
build or soak is planned.
