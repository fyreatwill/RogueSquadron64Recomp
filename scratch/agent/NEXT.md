# NEXT work unit (s894)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`streamSampleCountToByteSize` (`0x800981E4`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate every
argument transformation, table/record access, bound, sentinel/state check,
and writer basis. Do not add a guard until the whole class is enumerated. Do
not run a game build or animating A/B for this source inventory.

Competing hypotheses:

- H-stream-size-unclassified: at least one argument or derived size site lacks
  a proof of safety or a concrete writer/legitimacy basis.
- H-stream-size-fully-classified: every site in the candidate is bounded and
  its writers are proven legitimate.
- H-stream-size-shape-mismatch: the function mixes unrelated argument/table
  shapes;
  record the exact sites and stop rather than mixing shapes.

Discriminating measurement: a complete table of every
`streamSampleCountToByteSize` site, including guest address, operation,
derived value, bound/state check, and the writer that established each input.
Any omitted access or unproven writer rejects H-stream-size-fully-classified.

Exact commands: use `rg` to enumerate `streamSampleCountToByteSize` and its
`MEM_*`/`goto` sites in `../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded
`sed` windows and the companion `rogue_squadron64` symbol/decomp files. No
game build or soak is planned.
