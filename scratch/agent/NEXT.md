# NEXT work unit (s2904) — M4 producer/consumer index join

HYPOTHESIS-ID: m4-accumulator-boundary-revisit

Run the existing phase-gated M4 producer/consumer index join in one Debug
build/run. Capture the complete table of producer slot writes at overlay-0x1c
`B00/B02/B04`, the overlay-0x20 consumer index from the `C70/B74` path, and
the resulting selected slot, with the independent M4 arithmetic positive
control in the same run. Use the qualified LLE-only route and hangar origin;
do not add a new field or re-watch the closed `0x688:0x710`/`0xD60` source
questions.

## Competing hypotheses and discriminator

- H-IndexMatches: the consumer low-seven-bit index equals a producer slot in
  the target phase and the join reaches the shared consumer path.
- H-IndexMisses: producer slots are populated but the consumer index never
  matches them, explaining the unresolved accumulator boundary.
- H-NoProducer: the consumer path is live but no producer slot is published in
  the target phase.
- H-InstrumentAbsent: the independent arithmetic positive control fails; all
  M4 join nulls are unevaluable.

The single discriminator is one phase-keyed row set containing every producer
slot/value, every consumer index, selected-slot result, and the arithmetic
positive-control tuple. A nonzero changing arithmetic control is mandatory;
the producer and consumer rows must be compared in the same task/phase key.

## Exact commands

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_LOG_M4_INDEX=1 ROGUESQ_LOG_M4_ACCUM=1 \
  ROGUESQ_M4_Y8000_WIDTH=512 ROGUESQ_AUTOPILOT=1 \
  ./build/Debug/RogueSquadron64Recomp.exe > scratch/agent/s2904_m4_index_join/run.log 2>&1
```

Expected outcomes: positive-control rows select the instrument-valid branch;
matching producer/consumer keys select H-IndexMatches, producer rows without
a match select H-IndexMisses, consumer-only rows select H-NoProducer, and a
missing arithmetic control selects H-InstrumentAbsent. A mitigation or value
rewrite is forbidden without an `ORIGIN:` naming the legitimate writer.
