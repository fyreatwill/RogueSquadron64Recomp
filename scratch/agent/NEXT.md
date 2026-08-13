# NEXT work unit (s912)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`serviceVoicePoolFrame` (`0x8009B5A8`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate every voice-slot/table
load/store, control operation, dependent caller, and ownership basis. Do not
add a guard or change game behavior. Do not run a game build or animating A/B
for this source inventory.

Competing hypotheses:

- H-service-voice-pool-unclassified: the helper has an unchecked or aliasing-sensitive
  slot/list access whose writer/initialization obligation cannot be classified
  from the function and sibling writers.
- H-service-voice-pool-fully-classified: all slot/list reads and writes are bounded by
  the function's controls, and its callers agree on the same layout.
- H-service-voice-pool-shape-mismatch: callers use incompatible layouts or the helper's
  output aliases a state structure; record the exact split and stop.

Discriminating measurement: a complete site table for `serviceVoicePoolFrame`,
every slot/list load/store and control operation, all generated callers, and
the companion symbol/decomp basis. Any omitted access or incompatible caller
shape rejects full classification.

Exact commands: use `rg` to enumerate `serviceVoicePoolFrame` and its callsites
in `../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded `sed` windows and
the companion `rogue_squadron64` symbol/decomp files. No game build or soak is
planned.
