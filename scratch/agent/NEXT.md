# NEXT work unit (s914)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`loadSpeechFile` (`0x8009BA38`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate every speech-file state,
allocation, DMA/asset, voice-table, queue, and cleanup load/store, control
operation, dependent caller, and ownership basis. Do not add a guard or change
game behavior. Do not run a game build or animating A/B for this source
inventory.

Competing hypotheses:

- H-load-speech-unclassified: the loader mixes speech-file state, allocation,
  DMA/asset ownership, and voice-table teardown or setup paths whose bounds or
  writers cannot be classified from the function and sibling helpers.
- H-load-speech-fully-classified: all dynamic pointers, sizes, state gates, and
  cleanup paths have explicit controls, and companion callers agree on them.
- H-load-speech-shape-mismatch: callers or sibling helpers use incompatible
  asset/buffer layouts; record the exact split and stop.

Discriminating measurement: a complete site table for `loadSpeechFile`, every
speech-file state, allocation, DMA/asset, voice-table, queue, and cleanup
load/store and control operation, all generated callers, and the companion
symbol/decomp basis. Any omitted access or incompatible caller shape rejects
full classification.

Exact commands: use `rg` to enumerate `loadSpeechFile` and its callsites in
`../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded `sed` windows and the
companion `rogue_squadron64` symbol/decomp files. No game build or soak is
planned.
