# NEXT work unit (s886)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`tickScheduledSongEvents`'s `+0xE7C` linked-list insertion path in
`../N64Recomp/RecompiledFuncs/funcs_25.c`. Enumerate every chain site in the
complete function, classify predecessor checks and every pointer writer shared
with the song paths, and do not add a guard until the whole class is
enumerated. Do not run a game build or animating A/B for this source inventory.

Competing hypotheses:

- H-scheduled-unclassified: at least one pointer site lacks a proof of safety or
  a concrete writer/legitimacy basis.
- H-scheduled-fully-classified: every site in the candidate is bounded and its
  writers are proven legitimate.
- H-scheduled-shape-mismatch: the function mixes unrelated pointer shapes;
  record exact sites and stop there.

Discriminating measurement: a complete table of every `tickScheduledSongEvents`
`+0xE7C` pointer-chain site, including guest address, dereference offset,
preceding state/null check, and the writer that established each base pointer.
Any omitted access or unproven writer rejects H-scheduled-fully-classified.

Exact commands: use `rg` to enumerate `tickScheduledSongEvents` and its `MEM_*`/
`goto` sites in `../N64Recomp/RecompiledFuncs/funcs_25.c`, then bounded `sed`
windows and the companion `rogue_squadron64` symbol/decomp files. No game build
or soak is planned.
