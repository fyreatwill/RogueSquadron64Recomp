# NEXT work unit (s882)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`tickAudioChannel`'s program-stream cursor dereference class in
`../N64Recomp/RecompiledFuncs/funcs_23.c`. Enumerate every cursor read and
write in the complete function, classify its predecessor checks and cursor
writer/legitimacy, and do not add a guard until the whole class is enumerated.
Do not run a game build or animating A/B for this source inventory.

Competing hypotheses:

- H-cursor-unclassified: the function has at least one program-stream cursor
  dereference without a proof of safety or a concrete writer/legitimacy basis.
- H-cursor-fully-classified: every cursor use is bounded by the channel state
  machine and its writer is proven legitimate.
- H-cursor-shape-mismatch: the function mixes program-stream accesses with
  unrelated channel/global pointers; record exact sites and stop there.

Discriminating measurement: a complete table of every `ctx->r2`/derived cursor
`MEM_*` access in `tickAudioChannel`, including guest address, cursor offset,
preceding state/null check, and the writer that established `channel+0x4`.
Any omitted access or unproven writer rejects H-cursor-fully-classified.

Exact commands: use `rg` to enumerate `tickAudioChannel` and its `MEM_*`/
`goto` sites in `../N64Recomp/RecompiledFuncs/funcs_23.c`, then bounded `sed`
windows and the companion `rogue_squadron64` symbol/decomp files. No game build
or soak is planned.
