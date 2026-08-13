# NEXT work unit (s906)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`normalizeVec3` (`0x80099CFC`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate every listener/voice-list
or table access, vector load/store, dependent caller, and ownership basis.
Do not add a guard or change game behavior. Do not run a game
build or animating A/B for this source inventory.

Competing hypotheses:

- H-normalize-unclassified: the helper has an unchecked or aliasing-sensitive
  vector access whose caller-provided record shape cannot be established.
- H-normalize-fully-classified: all vector reads/writes are fixed-shape,
  bounded by the function's arithmetic, and its callers agree on the same
  layout.
- H-normalize-shape-mismatch: callers use incompatible vector layouts or the
  function's output aliases a state structure; record the exact split and
  stop.

Discriminating measurement: a complete site table for `normalizeVec3`, every
vector load/store and arithmetic operation, all generated callers, and the
companion symbol/decomp basis. Any omitted access or incompatible caller shape
rejects full classification.

Exact commands: use `rg` to enumerate `normalizeVec3` and its callsites in
`../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded `sed` windows and the
companion `rogue_squadron64` symbol/decomp files. No game build or soak is
planned.
