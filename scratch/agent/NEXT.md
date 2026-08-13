# NEXT work unit (s896)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`stopStreamedVoice` (`0x80098298`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate every
argument transformation, table/record access, bound, sentinel/state check,
and writer basis. Do not add a guard until the whole class is enumerated. Do
not run a game build or animating A/B for this source inventory.

Competing hypotheses:

- H-stop-streamed-unclassified: at least one memory access, derived pointer, or
  input value lacks a structural or writer/legitimacy basis.
- H-stop-streamed-fully-classified: all accesses and transformations are bounded,
  and every dynamic input has a concrete writer/legitimacy basis.
- H-stop-streamed-shape-mismatch: the function mixes unrelated voice/table shapes;
  record the exact sites and stop rather than mixing shapes.

Discriminating measurement: a complete table of every
`stopStreamedVoice` site, including guest address, operation, derived
value, bound/state check, and the writer that established each input. Any
omitted access or unproven writer rejects H-voice-pan-fully-classified.

Exact commands: use `rg` to enumerate `stopStreamedVoice` and its
`MEM_*`/`goto` sites in `../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded
`sed` windows and the companion `rogue_squadron64` symbol/decomp files. No
game build or soak is planned.
