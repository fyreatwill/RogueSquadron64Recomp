# NEXT work unit — bounded M5 direct DP-producer audit

HYPOTHESIS-ID: m5-route-direct-dp-producer

Audit the direct producer boundary before the DP consumer at `0x8001C38C`,
using `osSendMesg` (`0x80033410`) and queue `0x8011A408`. Session 3049 showed
the port's DP registration/completion path is live, while retail reaches the
target consumer without the watched DP-handler registration path. Do not repeat
the registration or consumer-only watches.

Competing hypotheses and the discriminator:

- H-DirectProducerMissing: retail has no target-phase direct send to the queue,
  while the port's event completion path is the only source.
- H-DirectProducerDivergent: retail has a target-phase direct send, but its
  caller, message, return, or ordering differs from the port.
- H-DirectProducerEquivalent: retail and port direct sends match; the VI-640
  boundary is elsewhere.
- H-MeasurementInsufficient: the retail attribution or port positive control
  cannot arm for the selected registration edge.

The single discriminator is a retail-vs-port table keyed by target-phase
`osSendMesg` caller, queue, message, return code, and ordering relative to the
next VI transition. No retail target-phase row selects H-DirectProducerMissing;
a row with differing caller/message/return/order selects
H-DirectProducerDivergent; matching rows plus target transition select
H-DirectProducerEquivalent; absent retail attribution or an unarmed port
control selects H-MeasurementInsufficient.

Commands:

1. Bounded static search:
   `rg -n -C 20 'osSendMesg|0x80033410|0x8011A408|8001C388|8001C38C' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs src /Users/williambuckley/Documents/Tools/rogue_squadron64`
2. Ask the retail oracle to watch `0x80033410`, always including
   `--watch-write 0x0:0x800000`, Rice video, the driven Start schedule,
   `--vi-trace`, and target-phase logging for `0x00790400:1024` and
   `0x006AB400:512`.
3. Only if retail attribution is positive, add one batched port probe, build
   with `cmake --build build --config Debug --target RogueSquadron64Recomp`,
   and run from `build/` with LLE-only AUTOPILOT and `ROGUESQ_LOG_PHASE=1`.

Expected outcomes: all four hypotheses must have a named observable outcome;
no behavior change is justified by a route-null or by event wiring alone.
