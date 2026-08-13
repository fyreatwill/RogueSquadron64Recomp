# NEXT work unit (s891)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`unloadLastSndFileGroup` (`0x800978EC`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate every song-bank/table
pointer access, record dereference, cursor advance, loop bound,
state/sentinel check, and writer basis. Do not add a guard until the whole
class is enumerated. Do not run a game build or animating A/B for this source
inventory.

Competing hypotheses:

- H-unload-snd-unclassified: at least one song-bank or record/cursor site
  lacks a proof of safety or a concrete writer/legitimacy basis.
- H-unload-snd-fully-classified: every site in the candidate is bounded and
  its writers are proven legitimate.
- H-unload-snd-shape-mismatch: the function mixes unrelated pointer shapes;
  record the exact sites and stop rather than mixing shapes.

Discriminating measurement: a complete table of every
`unloadLastSndFileGroup` pointer site, including guest address, dereference
offset, loop/state check, and the writer that established each base pointer.
Any omitted access or unproven writer rejects H-unload-snd-fully-classified.

Exact commands: use `rg` to enumerate `unloadLastSndFileGroup` and its
`MEM_*`/`goto` sites in `../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded
`sed` windows and the companion `rogue_squadron64` symbol/decomp files. No
game build or soak is planned.
