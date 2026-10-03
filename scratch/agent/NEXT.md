# Next work unit: qualify the retail image destination/writeback role

HYPOTHESIS-ID: m5-retail-image-destination-role

Run one paired retail/port oracle capture that keeps the exact task joins from
s3854 but measures the destination/writeback role directly. Use the known
stage PCs and their phase-gated live structures, plus a phase-gated watch of
the candidate destination span and the `0x1798B0` image output. Do not infer a
destination from the task pointer alone.

Competing hypotheses and discriminator:

- H1: retail stage activity writes a unique image destination/writeback tuple
  for one of the joined task-pointer classes.
- H2: retail stage activity is generic/alternate-object work and never reaches
  the qualified image destination span.
- H3: retail reaches the destination span, but the existing writer-PC and
  phase bucket are too coarse to identify the tuple.

The discriminator is one same-run paired capture passing whole-RDRAM, title/
hangar VI, and no-crash positive controls. H1 requires a task-pointer class
and writer event to share one destination/length tuple; H2 requires task rows
and stage activity with zero qualified destination-span writes; H3 requires
nonzero destination-span writes but multiple tuples after the combined join.

Starting commands:

    sed -n '1,260p' scratch/agent/run_s3854_m5_task_stage_data_join.sh
    # Extend the s3854 script with destination-span writer attribution, then:
    env zsh scratch/agent/run_s3855_m5_retail_destination_role.sh

Run both arms in that one script/build, phase-gated on VI transitions. Fold the
paired counts and destination tuple into the ledger; do not repeat the
descriptor-only watch or claim a destination from a broad range alone.
