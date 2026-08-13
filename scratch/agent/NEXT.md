# NEXT work unit (s915)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`initMusyXVoiceTable` (`0x8009BBA0`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate every speech-file state,
allocation, DMA/asset, voice-table, queue, and cleanup load/store, control
operation, dependent caller, and ownership basis. Do not add a guard or change
game behavior. Do not run a game build or animating A/B for this source
inventory.

Competing hypotheses:

- H-init-voice-table-unclassified: the initializer mixes bounded slot setup,
  queue creation/seeding, and global reset paths whose bounds or ownership are
  not independently established.
- H-init-voice-table-fully-classified: the slot count/stride, queue storage,
  reset fields, and caller contract are explicit and mutually consistent.
- H-init-voice-table-shape-mismatch: a caller or sibling helper uses an
  incompatible slot or queue layout; record the exact split and stop.

Discriminating measurement: a complete site table for `initMusyXVoiceTable`,
every slot/queue/global load/store and control operation, all generated callers,
and the companion symbol/decomp basis. Any omitted access or incompatible
caller shape rejects full classification.

Exact commands: use `rg` to enumerate `initMusyXVoiceTable` and its callsites in
`../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded `sed` windows and the
companion `rogue_squadron64` symbol/decomp files. No game build or soak is
planned.
