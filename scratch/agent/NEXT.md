# NEXT work unit — join controlled port schema to retail output/state rows

HYPOTHESIS-ID: m5-output-state-contract-boundary

Both port arms are now controlled: each emitted 2,048 schema rows and the
four-PC positive-control marker. The sequential arm difference is unusable as
an animated A/B. Join each port arm to the independent retail baseline by
phase, target PC, and ordinal. The oracle baseline is
`scratch/agent/s3450_oracle_fixed.log`.

Competing hypotheses and discriminating outcomes:

- `H-JoinParity`: ordered port/retail rows match through the target fields;
  close the qualified boundary.
- `H-FirstFieldDivergence`: the first mapped field differs with valid controls;
  that field selects the missing contract edge.
- `H-JoinMismatch`: controls fire but phase/PC/ordinal cannot join; redesign
  only the join key and make the rows unevaluable.
- `H-PortAbsent`: a selected port phase/PC bucket is absent despite the
  positive control; fix the phase mapping before interpreting parity.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    # Extract/join fresh port rows against scratch/agent/s3450_oracle_fixed.log
    # using phase, target PC, and ordinal; do not use sequential arm equality.

Keep waits, slots, dispatch, clear behavior, and PCM writeback unchanged.
