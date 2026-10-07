# Next work unit: requalify M5 Step 6 after tick-off route failure

HYPOTHESIS-ID: m5-step6-drain-tick-validation

Competing hypotheses and discriminator written before the next build:

- H-tick-required: the default drain-tick-off arm loses a required status/slot
  transition or downstream PCM contract, while the same-build tick-on arm
  preserves it.
- H-tick-not-required: both arms preserve task/SP completion, status/slot
  progress, nonzero PCM joins, and title/hangar phases.
- H-route-invalid: either arm misses a mandatory target phase or the whole
  positive-control route, making its downstream null unevaluable.

The single discriminating measurement is one same-build, phase-gated sequential
A/B using the existing three-arm harness (stub warmup, tick-on, then tick-off)
with `ROGUESQ_DRAIN_INLOOP_TICK=1` and `0`, joined by phase and arm across
task dispatch/exit, SP completion, status `01/02/00` and `03` reaping, PCM
source/consumer, and title/hangar VIs. A tick-only status/PCM loss selects
H-tick-required; matching complete rows select H-tick-not-required; a missing
control or target phase selects H-route-invalid and proves nothing downstream.

Exact command after the existing Debug build:
`env DRAIN_TICK_ORDER=legacy zsh scratch/agent/run_s2328_m5_drain_tick_ab.sh s4114_m5_drain_tick_requalify`.
Require the retail whole-RDRAM/title/hangar controls and retain 15 seconds
after hangar. Tick-only status/PCM loss selects H-tick-required; matching
qualified rows select H-tick-not-required; any pre-target arm failure selects
H-route-invalid and proves nothing downstream. Kill every process group with
SIGKILL.
