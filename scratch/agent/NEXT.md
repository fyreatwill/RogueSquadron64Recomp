# NEXT work unit — identify the M5 slot/status consumer boundary

HYPOTHESIS-ID: m5-step1-slot-status-consumer

Run one ground-truth-first discriminator for the target-phase slot/status
consumer boundary exposed by Session 3326. The candidate output spans had no
retail target-phase writes, but slot `0x141AD0:0x141AF0` and status
`0x154620:0x1546A0` did. Before building anything, use the oracle with the
whole-RDRAM control and watch those two ranges plus the named PCs
`0x80094648`, `0x8009B600`, `0x8009B85C`, `0x8009BDE8`. If the control is live,
build one port probe for the same ranges and run one phase-gated image arm.

## Competing hypotheses

- `H-RetailSlotConsumer`: retail slot/status writes are followed by the
  target consumer; the missing port edge is this contract relation.
- `H-RetailStatusOnly`: retail writes status without a target slot consumer;
  move upstream to the writer's input/dispatch relation.
- `H-PortMatchesRetail`: the qualified port has the same slot/status writer
  and order, so the current symptom is downstream.

## Discriminator

The oracle watch must pass the whole-RDRAM positive control and emit
target-phase slot/status writes with PC attribution. A slot write followed by
the named status/consumer order selects `H-RetailSlotConsumer`; status-only
activity selects `H-RetailStatusOnly`; matching writer/order rows in the
qualified port select `H-PortMatchesRetail`. A positive control without the
target slot/status activity is invalid for this unit.

## Exact starting checks

```sh
sed -n '1,220p' tools/oracle/README.md
rg -n 'slot|output|PCM|B40|route|candidate' docs/M5-AUDIO-PLAN.md docs/CURRENT-TRUTH.md
```

Then run the source-grounded oracle watch before any build. If its positive
control and target phase pass:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Use one phase-gated image-arm capture with all slot/status and PCM controls;
do not change behavior or add a mitigation.
