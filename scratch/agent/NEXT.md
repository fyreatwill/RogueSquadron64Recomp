# NEXT work unit (s889)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`processSongByHandle` (`0x800966A4`) in
`../N64Recomp/RecompiledFuncs/funcs_25.c`. Enumerate every cursor/table
slot/table pointer access, record dereference, loop bound, state/sentinel
check, and writer basis. Do not add a guard until the whole
class is enumerated. Do not run a game build or animating A/B for this source
inventory.

Competing hypotheses:

- H-process-song-unclassified: at least one handle-derived slot/table site
  lacks a proof of safety or a concrete writer/legitimacy basis.
- H-process-song-fully-classified: every site in the candidate is bounded and
  its writers are proven legitimate.
- H-process-song-shape-mismatch: the function mixes unrelated pointer shapes;
  record exact sites and stop there.

Discriminating measurement: a complete table of every `processSongByHandle`
pointer site, including guest address, dereference offset, loop/state check,
and the writer that established each base pointer. Any omitted access or
unproven writer rejects H-process-song-fully-classified.

Exact commands: use `rg` to enumerate `processSongByHandle` and its `MEM_*`/
`goto` sites in `../N64Recomp/RecompiledFuncs/funcs_25.c`, then bounded `sed`
windows and the companion `rogue_squadron64` symbol/decomp files. No game build
or soak is planned.
