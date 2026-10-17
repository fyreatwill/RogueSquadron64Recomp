# Next: per-task port-side M4 transient accumulator summary

Session 5279 corrected the retail decoder: `0x8000` is transient mid-task
VACC state in all 572 512-wide retail tasks, including both hangar origins,
but is absent from all task-end VACC records. Session 5280's qualified port
run found 18 sampled `0x8000` components in 2,000 phase-5 mid-task rows and
none in 352 task-end rows, but the row cap concentrated on one task. The
whole-RDRAM control and both VACC streams passed; the `0x80033FCC` publication watch did not fire and
must not be treated as a null result.

Competing hypotheses and discriminator:

- H1: most/all port hangar tasks have transient `0x8000`, like retail; the
  remaining M4 artifact is not an accumulator-origin difference.
- H2: only a minority of port tasks have the transient, or its first/last
  stage differs materially; the qualitative match is not enough.
- H3: the current positive rows came from an exceptional task and ordinary
  port tasks have no `0x8000`; the discrepancy remains in the port RSP/Factor 5
  path or task input.

Discriminating measurement: add a per-task accumulator summary that records
task id, whether any sampled lane has `0x8000`, and the first/last stage that
does, phase-gated to 512-wide hangar tasks. Retain the task-end row and phase
positive control in the same build/run. H1 predicts near-universal task
presence; H2 predicts a substantial but non-universal population or a
different stage window; H3 predicts presence only in the exceptional task.
Do not infer anything from the failed retail publication watch until its
execution positive control is repaired.

Preparation/search command:

`rg -n "VACC|rsp.*task|M_GFXTASK|0x8000|mid.*dump|task.*dump|whole-RDRAM" src lib tools scratch docs`

HYPOTHESIS-ID: m4-accumulator-boundary-revisit
