# Next work unit — RESUME

HYPOTHESIS-ID: ovl2c-real-splice

Resume the incomplete s4756 work unit. Do not rerun the experiment until the
generated tree is complete. Restore a snapshot containing both
`rs64_s4207_after_audtask` and `rs64_s4581_inflight`, or reconstruct exactly
those two durable definitions from their existing apply scripts. Do not invoke
the newer full N64Recomp regeneration; it reproduced the `after_0` truncation
hazard.

Then run exactly:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

If it links, use the s4753 direct mission driver with
`ROGUESQ_OVL2C_DROP=0`. The positive controls are VI 512 at `0x00690400` and
no crash/abort. Record per-task runaway count, the 0x2C route marker, and the
phase-gated mission frames.

Competing hypotheses and discriminator:

- H1: the real 0x2C image emits the missing billboard/sprite content while the
  DL remains bounded.
- H2: the splice has an ABI/table/extern mismatch and crashes or re-enters the
  restart loop.
- H3: the covered mission defects are unrelated to 0x2C.

DISCRIMINATING MEASUREMENT: one repaired binary and one phase-gated mission
capture. H1 predicts bounded 0x2C activity plus changed sprite content; H2
predicts a crash or runaway recurrence; H3 predicts the s4753 bounded route and
unchanged mission content. Current evidence selects none of these runtime
hypotheses.
