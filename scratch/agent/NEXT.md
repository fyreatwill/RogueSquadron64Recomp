# NEXT work unit (s916)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`findFreeSpeechVoiceSlot` (`0x8009BC88`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate every slot/global load,
active-byte test, nested-loop counter/control operation, return path, dependent
caller, sibling scan, and ownership basis. Do not add a guard or change game
behavior. Do not run a game build or animating A/B for this source inventory.

Competing hypotheses:

- H-free-speech-slot-unclassified: the helper's nested scan has an unproven
  termination/count contract or mixes incompatible voice-slot shapes.
- H-free-speech-slot-fully-classified: the one-slot scan, active-byte test,
  return contract, and sibling callers are explicit and mutually consistent.
- H-free-speech-slot-shape-mismatch: a caller or sibling helper supplies a
  different index/table contract; record the exact split and stop.

Discriminating measurement: a complete site table for
`findFreeSpeechVoiceSlot`, every slot/global load and control operation, all
generated callers, and the companion symbol/decomp basis. Any omitted access,
unbounded termination, or incompatible caller shape rejects full
classification.

Exact commands: use `rg` to enumerate `findFreeSpeechVoiceSlot` and its
callsites in `../N64Recomp/RecompiledFuncs/funcs_*.c`, then bounded `sed`
windows and the companion `rogue_squadron64` symbol/decomp files. No game build
or soak is planned.
