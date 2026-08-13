# NEXT work unit (s883)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`stopSongByHandle`'s pointer-chain dereference class in
`../N64Recomp/RecompiledFuncs/funcs_25.c`. Enumerate both chain sites in the
complete function, classify predecessor checks and every pointer writer, and
do not add a guard until the whole class is enumerated. Do not run a game build
or animating A/B for this source inventory.

Competing hypotheses:

- H-stop-song-unclassified: at least one chain site lacks a proof of safety or
  a concrete writer/legitimacy basis.
- H-stop-song-fully-classified: every chain site is bounded and its writers are
  proven legitimate.
- H-stop-song-shape-mismatch: the two sites are different pointer idioms and
  cannot form one coherent class; record exact sites and stop there.

Discriminating measurement: a complete table of both `stopSongByHandle`
pointer-chain sites, including guest address, dereference offset, preceding
state/null check, and the writer that established each base pointer. Any
omitted access or unproven writer rejects H-stop-song-fully-classified.

Exact commands: use `rg` to enumerate `stopSongByHandle` and its `MEM_*`/
`goto` sites in `../N64Recomp/RecompiledFuncs/funcs_25.c`, then bounded `sed`
windows and the companion `rogue_squadron64` symbol/decomp files. No game build
or soak is planned.
