# Next work unit: join retail writer callsites to task rows

HYPOTHESIS-ID: m5-task-output-contract-retail-callsite

Session 3848 was capture-valid. The exact retail watch
`0x167000..0x169B00` had phase writers `0x80015BC8` and `0x8000F3A0`, but
their live arguments described object/array activity rather than the port
stage-2 destination/length tuple. Retail had 1,142 task rows and no crash.

Before building anything, preserve these competing hypotheses and discriminator:

- H1: a writer callsite (`0x80015BC4` or `0x8000F39C`) carries a task pointer,
  destination, or length that joins a retail task generation to the port role.
- H2: the callsites remain bulk/object operations and carry no task join key.
- H3: callsite GPR rows are insufficient or unstable, so this route cannot
  measure exact retail task ownership.

Discriminating measurement: run one paired capture with the same whole-RDRAM,
title/hangar VI, type-2 task, and no-crash controls. Add `--watch-pc
0x80015BC4,0x8000F39C`, phase-gated to `0x00790400:1024` and
`0x006AB400:512`, while retaining the exact target watch and port stage logs.
H1 requires a stable callsite tuple or pointer joining task rows to the port
role; H2 requires controls but no tuple; H3 requires unstable or
uninterpretable callsite rows.

Starting command:

    zsh scratch/agent/run_s3849_m5_task_output_callsites.sh

Create that self-contained paired recipe from
`scratch/agent/run_s3848_m5_task_output_writer_args.sh`, changing only the
oracle watch PCs and bounded summary labels. Do not add a writeback guard or
infer a destination from the port address.
