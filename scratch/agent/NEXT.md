# NEXT work unit — trace the post-receive consumer/output edge

HYPOTHESIS-ID: m5-frequency-receive-consumer-contract

Session 3440 selected `H-RetailSendParity`: retail had 12,534
phase-qualified sends on `0x8010FEE0`, all `(queue,msg,flag)=(0x8010FEE0,0,0)`;
the port had 486 matching sends and 512 matching receives. Both port arms
consumed zero queue-head messages with live positive controls. The send
boundary is closed; do not infer that zero is corrupt.

Before building, ask ground truth for the selected consumer edge: run the
retail oracle with whole-RDRAM control, both title origins, hangar, and
`--watch-pc 0x80001B04,0x80001CB8,0x80006EFC,0x80006F5C`, phase-gated to the
same width/origin buckets. Then add one port post-receive consumer witness at
the first generated callsites after `osRecvMesg`, carrying the queue/message
join key and the first downstream state word. Keep the send/receive controls.

Competing hypotheses and the single discriminating measurement:

- `H-RetailConsumerParity`: zero messages reach matching downstream consumer
  state on retail and port; the gap is later.
- `H-PortConsumerStateGap`: both receive controls are live, but port diverges
  at the first consumer/output state after the matched zero message.
- `H-ConsumerUnevaluable`: retail consumer or port post-receive rows are absent
  despite live positive controls.

The measurement is the first post-receive consumer state tuple for the matched
`(0x8010FEE0,0,0)` message, compared against the same retail PC phase rows.
Matching state selects `H-RetailConsumerParity`; a live port receive followed
by divergent state selects `H-PortConsumerStateGap`; missing consumer rows
with live send/receive controls select `H-ConsumerUnevaluable`. Do not change
waits, slots, dispatch, clear behavior, or PCM writeback.

Build once with `cmake --build build --config Debug --target
RogueSquadron64Recomp`; run the oracle first, then concurrent silent/image port
arms from `build/` on the validated
`ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1` route. Use phase gates and SIGKILL
cleanup.
