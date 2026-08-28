# NEXT work unit — bounded M5 non-ProducerMark handoff audit

HYPOTHESIS-ID: m5-route-non-producermark-edge

Perform one new route-handoff measurement at a non-ProducerMark signal or
queue boundary different from the s3046 ProducerMark PCs and the s3047
frame-sync PCs. Start with a bounded static search for the next candidate, then
ask the retail oracle to attribute it before adding one batched port probe.
Retain whole-RDRAM and target-phase route controls; do not change behavior from
a route-null alone.

Competing hypotheses and the discriminator:

- H-NonProducerMarkMissing: a port producer/signal edge needed for the VI
  transition is absent or not delivered.
- H-NonProducerMarkWrongOrder: the edge exists but arrives in an order that
  prevents the target VI commit.
- H-NonProducerMarkEquivalent: the port edge matches retail and the blocker is
  elsewhere.
- H-MeasurementInsufficient: retail cannot independently attribute a new edge
  or the port positive control fails to arm.

The single discriminator is a retail-vs-port event table keyed to the next VI
transition: producer PC, signal/queue address, event payload, consumer PC, and
phase transition order. Missing producer/signal selects
H-NonProducerMarkMissing; matching events in the wrong order selects
H-NonProducerMarkWrongOrder; matching events and target transition select
H-NonProducerMarkEquivalent; absent retail attribution or an unarmed port
control selects H-MeasurementInsufficient.

Begin with a bounded search of the frame/DP/SP event and queue handoff code,
excluding `0x80019810`, `0x8001983C`, `0x80019868`, `0x8001BCE4`,
`0x8000C628`, and `0x8000BFE8`. Ask the retail oracle to watch the selected
candidate with a whole-RDRAM positive control and Rice video. Only then add a
single batched port probe.

The s3047 result was `H-MeasurementInsufficient`: the port probe positive
control fired, but the run stopped at VI 640 and produced no target-phase rows.
Do not reuse that null as evidence about the frame-sync edge.

Prior search shape:

    rg -n -C 20 'osViSetMode|osViSwapBuffer|osSendMesg|osRecvMesg|osJamMesg|ProducerMark|queue|signal' src lib /Users/williambuckley/Documents/Tools/rogue_squadron64

Record the complete table and decision in the new session evidence directory.
