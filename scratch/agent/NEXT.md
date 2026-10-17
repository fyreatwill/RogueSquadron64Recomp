# Next: port-side mid-task M4 accumulator capture

Session 5279 corrected the retail decoder: `0x8000` is transient mid-task
VACC state in all 572 512-wide retail tasks, including both hangar origins,
but is absent from all task-end VACC records. The whole-RDRAM control and
both VACC streams passed; the `0x80033FCC` publication watch did not fire and
must not be treated as a null result.

Competing hypotheses and discriminator:

- H1: the port has the same transient mid-task `0x8000` VACC state as retail;
  the remaining M4 artifact is not an accumulator-origin difference.
- H2: the port creates `0x8000` during mid-task execution but loses it before
  task end, while retail does the same; the task-end-only comparison hid a
  shared transient contract.
- H3: the port has no corresponding mid-task `0x8000`; the discrepancy is in
  the port RSP/Factor 5 implementation or task input before the accumulator.

Discriminating measurement: instrument the port’s graphics-task VACC state at
the same bounded mid-task cadence and phase-gate it to 512-wide hangar tasks,
while retaining the existing task-end row and a whole-RDRAM positive control
in one build/run. H1 predicts matching per-task mid-task lane presence and
task-end absence; H2 predicts both sides’ transient presence but different
timing/lifetime; H3 predicts zero port mid-task lanes despite retail’s
positive result. Do not infer anything from the failed retail publication
watch until its execution positive control is repaired.

Preparation/search command:

`rg -n "VACC|rsp.*task|M_GFXTASK|0x8000|mid.*dump|task.*dump|whole-RDRAM" src lib tools scratch docs`

HYPOTHESIS-ID: m4-accumulator-boundary-revisit
