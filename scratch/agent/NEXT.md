# Next work unit: join retail task-submission callers to task rows

HYPOTHESIS-ID: m5-task-output-contract-retail-submit-callers

Session 3849 was capture-valid. Whole-RDRAM and both target-VI controls fired;
retail had 1,138 type-2 task rows. The writer callsites were bulk/object
operations, so the next bounded join uses the task callee's observed
`PREVIOUS_PC` callers `0x80019DEC` and `0x80019D68`.

Before building anything, preserve these competing hypotheses and discriminator:

- H1: one submission caller carries a task pointer or destination/length that
  joins a retail task generation to the port role.
- H2: both callers are wrappers/loop machinery and carry no task join key.
- H3: caller GPR rows are unstable or insufficient, so exact ownership needs
  a different task-boundary instrument.

Discriminating measurement: run one paired capture with the same whole-RDRAM,
title/hangar VI, type-2 task, and no-crash controls. Replace the two writer
callsite watches with `--watch-pc 0x80019DEC,0x80019D68`, retaining the task
dump, exact target watch, and port stage logs. H1 requires a stable caller
tuple or pointer that joins task rows to the port role; H2 requires controls
but no tuple; H3 requires unstable or uninterpretable caller rows.

Starting command:

    zsh scratch/agent/run_s3850_m5_task_submit_callers.sh

Create that self-contained paired recipe from
`scratch/agent/run_s3849_m5_task_output_callsites.sh`, changing only the
oracle watch PCs, output directory, and bounded summary labels. Do not add a
writeback guard or infer a destination from the port address.
