# NEXT work unit — bounded M5 event-registration/wiring audit

HYPOTHESIS-ID: m5-route-event-registration-edge

Audit one new boundary before the DP consumer at `0x8001C38C`: the event
registration and delivery wiring for `OS_EVENT_DP` / queue `0x8011A408`.
Session 3048 proved the retail consumer is target-phase-active, while the port
only reached alternate pre-target queue consumers. Do not repeat the consumer
watch or infer a missing edge from that route-null.

Competing hypotheses and the discriminator:

- H-EventRegistrationMissing: the port does not register the DP event or queue
  wiring that retail uses.
- H-EventDeliveryWrong: registration exists, but the delivered event/message or
  ordering differs before the target VI transition.
- H-EventRegistrationEquivalent: registration and delivery match; the VI-640
  boundary is elsewhere.
- H-MeasurementInsufficient: the retail attribution or port positive control
  cannot arm for the selected registration edge.

The single discriminator is a retail-vs-port table keyed by event id, queue,
message, registration site, delivery site, and ordering relative to the next
VI transition. Missing registration selects H-EventRegistrationMissing;
matching registration with divergent delivery/order selects H-EventDeliveryWrong;
matching registration/delivery plus target transition selects
H-EventRegistrationEquivalent; absent retail attribution or an unarmed port
control selects H-MeasurementInsufficient.

Commands:

1. Bounded static search:
   `rg -n -C 20 'osSetEventMesg|OS_EVENT_DP|enqueue_external_message_src|events_context.dp|0x8011A408|dpInterruptHandlerThread' src lib /Users/williambuckley/Documents/Tools/rogue_squadron64`
2. Ask the retail oracle to watch the selected registration/delivery PC(s),
   always including `--watch-write 0x0:0x800000`, Rice video, the driven Start
   schedule, `--vi-trace`, and target-phase logging for
   `0x00790400:1024` and `0x006AB400:512`.
3. Only if retail attribution is positive, add one batched port probe in
   `src/main/upstream_compat.cpp`, build with
   `cmake --build build --config Debug --target RogueSquadron64Recomp`, and run
   from `build/` with LLE-only AUTOPILOT and `ROGUESQ_LOG_PHASE=1`.

Expected outcomes: all four hypotheses must have a named observable outcome;
no behavior change is justified by a route-null alone.
