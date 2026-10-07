# Next work unit: validate M5 Step 6 drain-tick removal

HYPOTHESIS-ID: m5-step6-drain-tick-validation

Competing hypotheses and discriminator written before the next build:

- H-tick-required: the default drain-tick-off arm loses a required status/slot
  transition or downstream PCM contract, while the same-build tick-on arm
  preserves it.
- H-tick-not-required: both arms preserve task/SP completion, status/slot
  progress, nonzero PCM joins, and title/hangar phases.
- H-route-invalid: either arm misses a mandatory target phase or the whole
  positive-control route, making its downstream null unevaluable.

The single discriminating measurement is one same-build, phase-gated A/B with
`ROGUESQ_DRAIN_INLOOP_TICK=1` and unset/default, joined by phase and arm across
task dispatch/exit, SP completion, status `01/02/00` and `03` reaping, PCM
source/consumer, and title/hangar VIs. A tick-only status/PCM loss selects
H-tick-required; matching complete rows select H-tick-not-required; a missing
control or target phase selects H-route-invalid and proves nothing downstream.

Exact work: use the qualified image route from
`scratch/agent/run_s4111_m5_image_preimage.sh`, retain the silent control only
as a same-build route sanity check if needed, and run both tick arms in one
build. Require the retail whole-RDRAM positive control if an oracle is paired;
kill every process group with SIGKILL. Enqueue the resulting phase-gated soak
instead of babysitting a repeat run.
