# NEXT work unit (s893)

HYPOTHESIS-ID: m3-idiom-inventory-next

Perform one bounded M3 idiom-class inventory in the generated game tree:
`flushStreamedVoiceBuffers` (`0x80097F54`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate every
slot/record pointer access, buffer/count argument, loop bound, state check, and
writer basis. Do not add a guard until the whole
class is enumerated. Do not run a game build or animating A/B for this source
inventory.

Competing hypotheses:

- H-flush-stream-unclassified: at least one slot/buffer/count site lacks a proof
  of safety or a concrete writer/legitimacy basis.
- H-flush-stream-fully-classified: every site in the candidate is bounded and
  its writers are proven legitimate.
- H-flush-stream-shape-mismatch: the function mixes unrelated pointer shapes;
  record the exact sites and stop rather than mixing shapes.

Discriminating measurement: a complete table of every
`flushStreamedVoiceBuffers` pointer site, including guest address, dereference
offset, loop/state check, and the writer that established each base pointer.
Any omitted access or unproven writer rejects H-flush-stream-fully-classified.

Exact commands: use `rg` to enumerate `flushStreamedVoiceBuffers` and its
`MEM_*`/`goto` sites in `../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded
`sed` windows and the companion `rogue_squadron64` symbol/decomp files. No
game build or soak is planned.
