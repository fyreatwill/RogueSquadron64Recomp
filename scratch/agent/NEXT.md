# Next work unit: join retail task data pointers to image-stage events

HYPOTHESIS-ID: m5-task-output-contract-retail-submit-callers

Session 3851 was capture-valid. Whole-RDRAM and both target-VI controls fired;
retail had 1,143 task rows. The descriptor had 44,270 writes from the same ten
PCs and a fixed 13-value schema. Input task pointers varied between
`0x80171E70`/`0x80173CB0`, but output and yield fields stayed zero. The
descriptor changes but does not expose a unique stage destination.

Before building anything, preserve these competing hypotheses and discriminator:

- H1: the task data pointer joins a unique image-stage/DMA event.
- H2: the task data pointer is reused or unrelated to image-stage ownership.
- H3: the pointer joins only a broad stage family; an event/generation key is
  still required.

Discriminating measurement: run one paired capture with the same whole-RDRAM,
title/hangar VI, type-2 task, and no-crash controls. Retain the task dump and
port stage logs, and phase-gated watch the task data-pointer destinations and
the exact image-stage DMA rows. H1 requires one pointer value to join a unique
stage event/generation; H2 requires no stable join; H3 permits a broad family
join but no unique event.

Starting command:

    zsh scratch/agent/run_s3852_m5_task_data_pointer_join.sh

Create that self-contained paired recipe from
`scratch/agent/run_s3851_m5_task_descriptor_writes.sh`, replacing the
descriptor-write-only discriminator with the task data-pointer/stage-event
join. Do not add a writeback guard or infer a destination from the port address.
