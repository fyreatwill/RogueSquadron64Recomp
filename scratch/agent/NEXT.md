# NEXT work unit (s908)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`invertOrientationMatrix` (`0x80099DCC`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate every listener/voice-list
or table access, vector load/store, dependent caller, and ownership basis.
Do not add a guard or change game behavior. Do not run a game
build or animating A/B for this source inventory.

Competing hypotheses:

- H-invert-unclassified: the helper has an unchecked or aliasing-sensitive
  vector access whose caller-provided record shape cannot be established.
- H-invert-fully-classified: all matrix/vector reads/writes are fixed-shape,
  bounded by the function's arithmetic, and its callers agree on the same
  layout.
- H-invert-shape-mismatch: callers use incompatible layouts or the
  function's output aliases a state structure; record the exact split and
  stop.

Discriminating measurement: a complete site table for `invertOrientationMatrix`, every
matrix/vector load/store and arithmetic operation, all generated callers, and the
companion symbol/decomp basis. Any omitted access or incompatible caller shape
rejects full classification.

Exact commands: use `rg` to enumerate `invertOrientationMatrix` and its callsites in
`../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded `sed` windows and the
companion `rogue_squadron64` symbol/decomp files. No game build or soak is
planned.
