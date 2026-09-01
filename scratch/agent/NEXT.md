# NEXT work unit — M5 selector-table writer-input producer boundary

HYPOTHESIS-ID: m5-selector-writer-input-producer

Session 3511 phase-matched the hangar stores. Retail and port agree on writer
PCs and stored values, but port already differs in writer `s1` (`0x5622` vs
retail `0x561F`). Trace the producer feeding that context before the two table
stores; do not repeat the completed store census.

Competing hypotheses and discriminating measurement:

- `H-ContextProducerParity`: writer context matches after the next producer;
  the remaining difference is earlier state initialization.
- `H-ContextProducerDivergence`: the next predecessor supplies different
  `s1`/context, selecting that producer edge.
- `H-LaterContextMutation`: predecessor context matches but a later guest
  instruction mutates it before the writer.
- `H-CaptureInvalid`: a same-run positive control or phase-matched writer
  control fails, making the comparison unevaluable.

Discriminating measurement: one independent retail capture and one qualified
port capture with positive controls, predecessor register/context rows, and
the existing phase-matched stores. Join by hangar origin, writer PC, store
ordinal, value, and predecessor-to-writer context. Matching predecessor fields
with a later writer difference selects a later mutation; the first differing
predecessor field selects its producer; failed controls make it unevaluable.

Before building, ask the independent retail oracle for the predecessor
boundary and whole-RDRAM control. Then add one regeneration-safe port witness
at that predecessor and run the validated real-image/LLE/spin-yield/autopilot
route with title and hangar buckets. Do not repeat the unchanged store census.

Expected outcomes: positive controls plus matching predecessor context selects
an intervening mutation or initializer; the first differing predecessor field
selects its producer; any missing control makes the join unevaluable.
