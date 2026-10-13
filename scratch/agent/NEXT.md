# Next work unit

HYPOTHESIS-ID: ovl2c-real-splice

Work unit: land the real overlay-0x2C RSPRecomp splice and validate it once.
This is currently blocked on the human allow rule for the RSPRecomp command;
do not retry the denied command in this iteration. If the allow rule is added,
run the existing fixup-6r draft, rebuild, then use the s4753 direct mission
driver with `ROGUESQ_OVL2C_DROP=0`.

Competing hypotheses and discriminator:

- H1: the real 0x2C image restores billboard/sprite content without reviving
  the runaway DL loop.
- H2: the splice has an ABI/table/extern mismatch and crashes or re-enters the
  restart loop.
- H3: the currently visible mission defects are unrelated to 0x2C.

DISCRIMINATING MEASUREMENT: one rebuilt binary, one mission capture, with
positive controls for VI `512 @ 0x00690400`, no crash/abort, and runaway-task
count. H1 predicts mission frames plus bounded 0x2C activity; H2 predicts a
crash or runaway recurrence; H3 predicts the same bounded route and unchanged
ship/HUD/terrain result as s4753.
