# Next work unit: join retail task data pointers to the image-stage event

HYPOTHESIS-ID: m5-retail-task-stage-data-pointer-join

Run one paired retail/port oracle capture extending the existing task-submission
probe. Join each retail task input pointer written into `0x80149470`
(`0x80171E70`, `0x80173CB0`, and related stage pointers) to the nearest
qualified image-stage/DMA event and its destination/length. Do not watch the
descriptor fields alone again.

Competing hypotheses and discriminator:

- H1: a task data pointer identifies the image-stage source/route and joins to a
  unique destination/length event.
- H2: task data pointers are reused generic inputs; no unique stage event joins.
- H3: the retail route reaches stage activity, but the event window is too
  coarse and needs a different independent boundary.

The discriminator is one same-run paired capture passing whole-RDRAM, title/
hangar VI, and no-crash positive controls. H1 requires the same task-pointer
generation to join one destination/length tuple; H2 requires qualified task
rows with no unique join; H3 requires stage activity with ambiguity after the
combined capture.

Starting commands:

    sed -n '1,240p' scratch/agent/run_s3851_m5_task_descriptor_writes.sh
    cp scratch/agent/run_s3851_m5_task_descriptor_writes.sh scratch/agent/run_s3854_m5_task_stage_data_join.sh
    # Edit the copy with apply_patch: retain all controls and add the task-pointer-to-stage/DMA join.
    env zsh scratch/agent/run_s3854_m5_task_stage_data_join.sh

Run both arms in that one script/build, phase-gated on VI transitions. Fold the
paired counts and join result into the ledger; do not repeat the descriptor-only
watch or claim a destination from a broad range alone.
