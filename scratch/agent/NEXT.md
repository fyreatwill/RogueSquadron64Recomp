# NEXT work unit (s2325) — M5 task/output-to-consumer join

HYPOTHESIS-ID: m5-task-output-consumer-join

## Work unit

Build one ground-truth-first table that joins the retail task/output writer
class to the port's rotating Factor 5 image-stage destinations. Run the retail
oracle first with its whole-RDRAM control and target-phase writer PCs, then run
stub and image arms from the same qualified eleven-Start route. This is one
measurement; do not change dispatch, writeback, slots, gates, waits, guards,
or defaults.

## Competing hypotheses and discriminating measurement

- H-Retail-Port-Shared-Output: the retail task/output writer class and the
  port image-stage row represent the same semantic buffer. A target-phase
  retail writer row and a port destination row can be joined by phase, width,
  ordinal/delta, length, payload hash/nonzero span, and source/consumer order.
- H-Port-Image-Stage-Only: the port image arm reaches the image DMA edge, but
  its nonzero or zero payload is not consumed by the downstream PCM/slot
  contract. The table has image-stage rows without an exact source/consumer
  or slot/descriptor row, while the stub has no image-stage rows.
- H-Destination-Role-Skew: the rotating physical destinations are distinct
  roles. One destination is stage-only while another has an exact source and
  consumer join, even when the image-stage payload tuple is otherwise equal.
- H-CoverageInvalid: the oracle whole-RDRAM control, target-phase writer
  bucket, or either port title/hangar phase is missing; no join or null is
  admissible.

The discriminator is one same-run table keyed by
`(source=retail|port, arm, phase, VI ordinal, origin, width, writer PC,
task/output address and length, image-stage destination and length, payload
FNV/nonzero, DMA ordinal/delta, PCM source ordinal, PCM consumer ordinal,
slot/status/descriptor row, route state)`. The oracle positive control must
precede narrow interpretation. A complete exact row selects
H-Retail-Port-Shared-Output; target coverage with image-stage but no exact
downstream row selects H-Port-Image-Stage-Only; two target destinations with
different stage-only versus source/consumer outcomes selects
H-Destination-Role-Skew; missing controls selects H-CoverageInvalid.

## Exact commands

Create the self-contained launcher with both port arms and the oracle gate,
then run it from the repository root:

    zsh -n scratch/agent/run_s2325_m5_task_output_join.sh
    zsh scratch/agent/run_s2325_m5_task_output_join.sh s2325_m5_task_output_join

The launcher must arm whole-RDRAM before narrow watches, include retail
`0x80094648`, `0x8008EB8C`, and `0x8008EBBC` writer controls plus the existing
gate/task/status controls, phase-gate all port rows at title/hangar VI
transitions, run stub and image arms in one build, SIGKILL every process group,
and emit the complete table before classifying the four outcomes.
