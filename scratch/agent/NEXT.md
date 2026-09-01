# NEXT work unit — M5 selector-table writer-input producer boundary

HYPOTHESIS-ID: m5-selector-writer-input-producer

Session 3513 was maintenance-only. Session 3512 showed that the guessed retail
predecessor PCs were not observable as execution callbacks even though the
selector stores were live. Do not repeat `0x8008F0A0`, `0x8008F1F0`, or
`0x80091934`.

Before building, ask the independent retail oracle for a genuinely new
producer/context boundary. Retain the whole-RDRAM positive control and selector
store control. Add one regeneration-safe port witness at that same boundary,
then run the validated real-image/LLE/spin-yield/autopilot route with title and
hangar buckets. Do not repeat the unchanged store census.

Competing hypotheses:

- `H-ContextProducerParity`: predecessor context matches; the difference is an
  earlier initializer or later mutation.
- `H-ContextProducerDivergence`: the predecessor supplies different `s1` or
  related context, selecting that producer edge.
- `H-LaterContextMutation`: predecessor context matches but an intervening
  guest instruction mutates it before the writer.
- `H-CaptureInvalid`: a same-run positive control or phase-matched writer
  control fails, making the join unevaluable.

Discriminating measurement: one independent retail capture and one qualified
port capture with the new predecessor rows, existing controls, and the two
phase-matched stores. Join by hangar origin, writer PC, store ordinal, value,
and predecessor-to-writer context. Matching predecessor fields with a later
writer difference selects a later mutation; the first differing predecessor
field selects its producer; failed controls select capture invalidity only.

Exact commands must be taken from the existing oracle/port recipe after the
new boundary is identified. Capture paths must have a non-dot final component;
run from `build/` and kill with SIGKILL.
