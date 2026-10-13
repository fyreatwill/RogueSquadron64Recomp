# Next work unit

HYPOTHESIS-ID: ovl2c-real-splice

Work unit: recover the complete current generated-function tree, rebuild, and
run the already-landed overlay-0x2C splice once. Do not invoke the newer full
N64Recomp regeneration again: it reproduced the `after_0` truncation hazard.
Restore only from a snapshot that contains both current diagnostic exports
`rs64_s4207_after_audtask` and `rs64_s4581_inflight`, or reconstruct those two
durable generated definitions from their existing apply scripts before building.
Then run:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Use the s4753 direct mission driver with `ROGUESQ_OVL2C_DROP=0`. Positive
controls are VI 512 at `0x00690400` and no crash/abort; collect per-task
runaway count and the 0x2C route marker.

Competing hypotheses and discriminator:

- H1: the real 0x2C image emits the missing billboard/sprite content while the
  DL remains bounded.
- H2: the splice has an ABI/table/extern mismatch and crashes or re-enters the
  restart loop.
- H3: the covered mission defects are unrelated to 0x2C.

DISCRIMINATING MEASUREMENT: one repaired binary and one phase-gated mission
capture. H1 predicts bounded 0x2C activity plus changed sprite content; H2
predicts a crash or runaway recurrence; H3 predicts the s4753 bounded route and
unchanged mission content. The prior iteration proved the splice source and
fixup compile, but not this runtime split.
