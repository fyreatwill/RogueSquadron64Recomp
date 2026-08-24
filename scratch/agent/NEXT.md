# NEXT work unit (s2328) — M5 drain-tick de-stubbing A/B

HYPOTHESIS-ID: m5-drain-tick-destub-ab

## Work unit

Execute the next bounded step in `docs/M5-AUDIO-PLAN.md`: compare the
existing in-loop `tickMusyXIfActive` injection with `ROGUESQ_DRAIN_INLOOP_TICK=0`
in one build, retaining the qualified image route and the silent control. This
is an A/B experiment only; do not promote a default or alter a slot, guard,
writeback, or gate.

## Competing hypotheses and discriminating measurement

- H-DrainRequired: the injected drain tick supplies the observed audio/slot
  progress. Turning it off removes a positive task/PCM/slot signal or loses
  the qualified title/hangar route.
- H-DrainRedundant: the injection is not required for the real task contract.
  Both tick arms retain title/hangar, task/DMA/image/PCM controls, and the same
  ordinal lifecycle table.
- H-DrainChangesOrdering: the injection preserves the route but moves the
  lifecycle relative to task start/stage/PCM. The signed ordinal table changes
  while route controls remain positive.
- H-CoverageInvalid: the retail oracle, either tick arm, or the required phase
  controls fail; no de-stubbing conclusion is admissible.

The discriminator is one phase-gated table keyed by `(tick arm, audio ordinal,
row, stage event, completion event, PCM source/consumer, slot/key-on/descriptor
event, signed delta to task begin and image stage)`, with both tick arms from
the same binary and the existing stub/image controls retained.

## Exact commands

First create the self-contained launcher
`scratch/agent/run_s2328_m5_drain_tick_ab.sh`, with two image arms that pass
`ROGUESQ_DRAIN_INLOOP_TICK=1` and `=0`, the existing eleven-Start schedule,
SIGKILL cleanup, and the oracle gate. Then run:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh -n scratch/agent/run_s2328_m5_drain_tick_ab.sh
    zsh scratch/agent/run_s2328_m5_drain_tick_ab.sh s2328_m5_drain_tick_ab

Require the oracle whole-RDRAM positive control, title/hangar VI transitions,
`[vi-callers-control]`, `[audtask-abi]`, image-stage/DMA, PCM source/consumer,
`[audio-sp-route] edge=guest-receive`, and the lifecycle join control in both
tick arms. Use SIGKILL for every cleanup. Do not interpret a filter/voice null
without its same-arm positive control.
