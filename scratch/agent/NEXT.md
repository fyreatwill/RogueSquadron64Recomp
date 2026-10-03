# Next work unit: qualify the retail side of the M5 image task/output edge

HYPOTHESIS-ID: m5-retail-image-task-output-edge

Run the paired capture from the repository root:

    zsh scratch/agent/run_s3855_m5_retail_destination_role.sh

Retain the whole-RDRAM positive control, title/hangar VI controls, and
no-crash/no-abort markers. Extend the oracle arm only if needed to join one
task generation to one candidate output destination; do not add a mitigation
or infer ownership from the port address.

Competing hypotheses and discriminator:

- H1: a retail task generation directly owns the candidate image-stage/output
  span and joins to a unique destination/length tuple.
- H2: retail reaches the stage writers but the task descriptor is generic; a
  separate writer owns publication, as in the qualified port edge.
- H3: the retail arm fails its positive control or target VI, making a null
  destination result unevaluable.

The discriminator is one paired capture with both target-VI controls and a
phase-gated task-generation-to-destination join. H1 requires a stable unique
tuple; H2 requires live task and writer rows without a unique tuple; H3 is
selected only when the controls fail.
