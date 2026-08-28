# NEXT work unit — bounded M5 route producer/signal audit

HYPOTHESIS-ID: m5-route-new-producer-edge

Perform one new route-handoff measurement tied to the retail-attributed
ProducerMark callers (`0x80019DEC`/`0x80019D68` precede the SP submit path).
Ask retail ground truth first, then add one batched port probe only if the
oracle identifies a distinct producer/signal edge. Retain whole-RDRAM and
target-phase route controls; do not change behavior from a route-null alone.

Competing hypotheses and the discriminator:

- H-ProducerSignalMissing: a port producer/signal edge needed for the VI
  transition is absent or not delivered.
- H-ProducerSignalWrongOrder: the edge exists but arrives in an order that
  prevents the target VI commit.
- H-ProducerSignalEquivalent: the port edge matches retail and the blocker is
  elsewhere.
- H-MeasurementInsufficient: retail cannot independently attribute a new edge
  or the port positive control fails to arm.

The single discriminator is a retail-vs-port producer/signal event table keyed
to the next VI transition: producer PC, signal/queue address, event payload,
consumer PC, and phase transition order. Missing producer/signal selects
H-ProducerSignalMissing; matching events in the wrong order selects
H-ProducerSignalWrongOrder; matching events and target transition select
H-ProducerSignalEquivalent; absent retail attribution or an unarmed port
control selects H-MeasurementInsufficient.

Exact pre-instrument commands from the repo root:

    rg -n -C 25 'bufferArbiterProducerMark|0x80019DEC|0x80019D68|VI|queue|signal' tools/oracle /Users/williambuckley/Documents/Tools/rogue_squadron64
    git diff -- src lib syms tools

Record the complete table and decision in
`scratch/agent/s3046_m5_route_producer_edge/`.
