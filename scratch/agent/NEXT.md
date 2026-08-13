# NEXT work unit (s892)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`serviceStreamedVoices` (`0x80097DA8`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate every
stream/voice-table pointer access, record dereference, cursor advance, loop bound,
state/sentinel check, and writer basis. Do not add a guard until the whole
class is enumerated. Do not run a game build or animating A/B for this source
inventory.

Competing hypotheses:

- H-service-stream-unclassified: at least one stream/voice-table or record/cursor site
  lacks a proof of safety or a concrete writer/legitimacy basis.
- H-service-stream-fully-classified: every site in the candidate is bounded and
  its writers are proven legitimate.
- H-service-stream-shape-mismatch: the function mixes unrelated pointer shapes;
  record the exact sites and stop rather than mixing shapes.

Discriminating measurement: a complete table of every
`serviceStreamedVoices` pointer site, including guest address, dereference
offset, loop/state check, and the writer that established each base pointer.
Any omitted access or unproven writer rejects H-service-stream-fully-classified.

Exact commands: use `rg` to enumerate `serviceStreamedVoices` and its
`MEM_*`/`goto` sites in `../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded
`sed` windows and the companion `rogue_squadron64` symbol/decomp files. No
game build or soak is planned.
