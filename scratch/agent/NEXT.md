# NEXT work unit (s2364) — M5 post-task publication/completion join

HYPOTHESIS-ID: m5-stage-output-contract-join

## Work unit

Run one same-build refinement of the existing stub/image pair. Retain every
s2361/s2363 route, oracle, VI, task-ABI, image-stage, service/slot,
filter/voice, PCM, and crash/abort control. Join each target stage's exact DMA
tuple to post-task source/consumer PCM rows and the containing task's later
completion/publication update. Do not change task data, field writeback,
consumer/default behavior, or add a guard.

## Competing hypotheses and discriminating measurement

- H-PostTaskPublicationClosed: the exact containing-task DMA tuple is followed
  by matching nonzero source and consumer rows plus a completion/publication
  update in the expected order.
- H-ContainingTaskInternalOnly: the exact stage/DMA relation remains visible,
  but post-task source/consumer or completion/publication does not close.
- H-TimingCaptureInvalid: a required oracle, route, stage, or positive control
  is absent; no contract conclusion is valid.

The discriminator is one complete table with every target-stage row, its
containing task ordinal, exact DMA tuple, post-task source/consumer tuples,
completion/publication event, and ordering deltas. Select one hypothesis only
if both arms retain the positive controls and the table is nonempty.

Implementation note before build: extend the persistent parser and driver in
one batch to retain the s2363 exact DMA match, then join that tuple's
post-task PCM source/consumer events and latest containing-task completion
record. Exact nonzero source plus consumer plus completion/publication ordering
selects H-PostTaskPublicationClosed; otherwise select
H-ContainingTaskInternalOnly; any missing control selects
H-TimingCaptureInvalid.

## Exact commands

    apply_patch < persistent post-task publication parser and driver patch
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2364_m5_post_task_publication_join.sh s2364_m5_post_task_publication_join
    grep -E '^(controls|table|verdict) ' scratch/agent/s2364_m5_post_task_publication_join/driver.log

The driver must run the retail oracle before the port arms, launch both arms
from the same build, use VI-gated controls, and kill game processes with
SIGKILL. Reject any null result without same-run positive controls.
