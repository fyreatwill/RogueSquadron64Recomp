# NEXT work unit (s1159)

HYPOTHESIS-ID: post640-selector-consumer-order

Run one phase-gated consumer-order capture after the reproduced post-640
selector transition. Instrumentation already present in the generated probe
must retain the independent selector-positive and slot-dispatch controls,
then correlate `selectAndApplyViMode`'s selector bytes and selected source
record with the copied record and the following host `osViSetMode` request.

Competing hypotheses and discriminator:

- H1: the selector transition is consumed correctly; the selected source
  record and copied record correspond to the new 640 descriptor, followed by
  a matching host request.
- H2: the consumer runs but selects a stale/wrong source record or copies the
  wrong record, so the host request does not match the new selector.
- H3: the consumer is not reached after the transition; host VI activity is
  independent of the generated selector path.

The discriminating measurement is one ordered post-640 table containing
selector bytes at consumer entry, selected source address/width, copied-record
address/width, and the next host VI request. The selector-positive and
slot-dispatch controls must fire; without them the result is inconclusive.

Commands:

    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
    env PROBE_PHASE_WIDTH=640 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 ROGUESQ_LOG_VI_WRITERS=1 ROGUESQ_LOG_VI_SELECTOR=1 ROGUESQ_LOG_SLOT_DISPATCH=1 ROGUESQ_LOG_VI_TRANSITION=1 zsh tools/probe.sh scratch/agent/s1159_selector_consumer_order 180 0.5

Expected outcomes: H1 closes the selector-consumer boundary for this path;
H2 identifies a stale/wrong source-record consumer; H3 sends the next audit
to the generated caller path. Do not infer parser or renderer causality from
a missing later VI phase.
