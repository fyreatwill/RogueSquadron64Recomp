# NEXT work unit (s888)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`advanceSongRegion` (`0x80095244`) in
`../N64Recomp/RecompiledFuncs/funcs_25.c`. Enumerate every cursor/table
pointer access, event-stream
deref, sentinel check, and writer basis. Do not add a guard until the whole
class is enumerated. Do not run a game build or animating A/B for this source
inventory.

Competing hypotheses:

- H-advance-region-unclassified: at least one cursor/table site lacks a proof
  of safety or a concrete writer/legitimacy basis.
- H-advance-region-fully-classified: every site in the candidate is bounded and
  its writers are proven legitimate.
- H-advance-region-shape-mismatch: the function mixes unrelated pointer
  shapes; record exact sites and stop there.

Discriminating measurement: a complete table of every `advanceSongRegion`
pointer/cursor site, including guest address, dereference offset, sentinel or
state check, and the writer that established each base pointer. Any omitted
access or unproven writer rejects H-advance-region-fully-classified.

Exact commands: use `rg` to enumerate `advanceSongRegion` and its `MEM_*`/
`goto` sites in `../N64Recomp/RecompiledFuncs/funcs_25.c`, then bounded `sed`
windows and the companion `rogue_squadron64` symbol/decomp files. No game build
or soak is planned.
