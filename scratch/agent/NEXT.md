# Next work unit: qualify retail task-descriptor field writes

HYPOTHESIS-ID: m5-task-output-contract-retail-submit-callers

Session 3850 was capture-valid. Whole-RDRAM and both target-VI controls fired;
retail had 1,313 task rows. `0x80019DEC` directly preceded the task callee with
`a0=0x80149470`, while `0x80019D68` carried stable `a0=0x800377C8`. The task
descriptor is reused and its output fields stayed zero, so the exact stage
destination is still unresolved.

Before building anything, preserve these competing hypotheses and discriminator:

- H1: writes into the task descriptor carry a changing destination/length or
  generation-specific join key.
- H2: descriptor writes are constant initialization or absent; the task boundary
  exposes no stage ownership.
- H3: descriptor fields change but are not sufficient, so ownership needs a
  different task-boundary instrument.

Discriminating measurement: run one paired capture with the same whole-RDRAM,
title/hangar VI, type-2 task, and no-crash controls. Add the physical descriptor
watch `--watch-write 0x149470:0x1494B0`, retaining both caller watches, task
dump, exact target watch, and port stage logs. H1 requires a descriptor field
write whose value/ordinal changes with task rows and joins the port role; H2
requires no writes or constant-only initialization; H3 requires changing but
uninterpretable fields.

Starting command:

    zsh scratch/agent/run_s3851_m5_task_descriptor_writes.sh

Create that self-contained paired recipe from
`scratch/agent/run_s3850_m5_task_submit_callers.sh`, adding only the descriptor
write watch, output directory, and bounded summary label. Do not add a
writeback guard or infer a destination from the port address.
