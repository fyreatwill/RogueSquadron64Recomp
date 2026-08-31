# NEXT work unit — trace the downstream producer after the joined clear

HYPOTHESIS-ID: m5-downstream-producer-edge

Session 3410 closed the input-to-clear edge: the port stores the expected
hangar field `0x801797B0`, and `0x8008F2CC` clears it on the same route ordinal.
Stage 3 then copies zero DMEM to `0x801798B0`, while retail publishes nonzero
target data.

Competing hypotheses:

- `H-PortIndirectProducerMissing`: the port lacks the retail-equivalent
  indirect `0x8002BEEC -> 0x800078EC` producer edge.
- `H-PortProducerRunsWrongRoute`: the producer runs, but outside the target
  route or before the joined clear.
- `H-PortImageSourceStillZero`: the producer edge is present and ordered, but
  its source input is already zero.

Discriminator: enumerate all generated/indirect executions feeding the target
producer in one phase-qualified census, joining producer PC, route ordinal,
clear ordinal, stage-3 ordinal, and source/destination payload hashes. Require
same-run whole-RDRAM, title/hangar, ABI/DMA, image-stage, and PCM controls.
A missing matching producer edge selects `H-PortIndirectProducerMissing`; a
matching edge with a different ordinal selects `H-PortProducerRunsWrongRoute`;
a matching ordered edge with zero source selects `H-PortImageSourceStillZero`.

Run from the repo root:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Use a new phase-scoped census script based on
`scratch/agent/run_s3409_m5_052c4_join.sh`, with silent/image arms together.
Do not change waits, slots, dispatch, clear behavior, or PCM writeback.
