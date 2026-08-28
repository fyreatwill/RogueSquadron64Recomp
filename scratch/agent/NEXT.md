# NEXT work unit — bounded M5 external DP-delivery audit

HYPOTHESIS-ID: m5-route-external-dp-delivery

Audit the external writer/delivery boundary that populates DP queue
`0x8011A408` before consumer `0x8001C38C`. Session 3050 found zero
target-phase direct `osSendMesg` sends to that queue in both retail and port;
do not repeat direct-send, registration, or consumer-only watches.

Competing hypotheses and the discriminator:

- H-ExternalDeliveryMissing: retail's DP interrupt/external enqueue path has a
  target-phase writer or delivery that the port does not reproduce.
- H-ExternalDeliveryDivergent: both paths deliver externally, but queue state,
  message, timing, or source differs at the target consumer.
- H-ExternalDeliveryEquivalent: external delivery and queue state match; the
  VI-640 boundary is elsewhere.
- H-MeasurementInsufficient: retail attribution or the port positive control
  cannot arm.

The single discriminator is a retail-vs-port table keyed by external writer or
interrupt source, queue mutation/delivery, message, queue validCount/first,
consumer PC, and ordering relative to the next VI transition. A retail row
with no corresponding port delivery selects Missing; differing state/order
selects Divergent; matching delivery plus target transition selects Equivalent;
an absent retail attribution or unarmed port control selects Insufficient.

Commands:

1. Static search:
   `rg -n -C 20 'dp_complete|enqueue_external|OS_EVENT_DP|8011A408|8001C38C|dpInterrupt' src lib /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs`
2. Ask the retail oracle to watch the candidate external writer PCs, always
   including `--watch-write 0x0:0x800000`, Rice video, the driven Start
   schedule, `--vi-trace`, and target-phase logging for
   `0x00790400:1024` and `0x006AB400:512`.
3. Only if retail attribution is positive, add one batched port probe, build
   with `cmake --build build --config Debug --target RogueSquadron64Recomp`,
   and run from `build/` with LLE-only AUTOPILOT and `ROGUESQ_LOG_PHASE=1`.

Expected outcomes: each hypothesis must receive a named observable outcome;
no behavior change is justified by another route-null or by event wiring alone.
