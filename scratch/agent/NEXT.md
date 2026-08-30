# NEXT work unit — attribute the retail pre-title route-state writer

HYPOTHESIS-ID: retail-pretitle-route-state-writer

The local guard-build attempt in Session 3251 was the third stalled attempt on
the same unavailable-host hypothesis. Do not repeat it locally. The next
single work unit is the independent-retail route-state attribution at the
pre-title 640-to-1024 boundary, centered on `reapplyDisplayMode` entry and
call (`0x8008EB5C`, `0x8008EBC0`) and its return branch (`0x8008EBC8`). This is
ground truth first; do not add port instrumentation or change audio behavior.

## Competing hypotheses

- `H-RetailWriterLiveAndAligned`: the watched retail writer/call/return edge
  fires at the target transition with ordered values comparable to the port's
  existing route/audio-return row.
- `H-RetailWriterAbsent`: the whole-RDRAM positive control and title gate pass,
  but this candidate edge does not execute; the candidate is ruled out.
- `H-RetailWriterMisaligned`: the edge fires, but its phase, arguments, or
  return value cannot explain the port boundary; redesign the join rather than
  adding a port counter.

## Discriminator

One oracle run with a whole-RDRAM positive control and title 1024 gate must
capture the writer/call/return PCs, live arguments, return branch, VI origin,
framebuffer context, and ordering at the 640-to-1024 transition.
`H-RetailWriterLiveAndAligned` requires the oracle watch sequence and a
comparison with the existing port row. A missing or misaligned candidate does
not authorize port instrumentation or an audio change.

## Exact commands

1. Read `tools/oracle/README.md` and use its existing route-watch recipe; do
   not build a new instrument before the oracle control is armed.
2. Run one retail capture with whole-RDRAM control, the three candidate PCs,
   and the title 1024 gate. Capture bounded output and classify the hypotheses.
3. Compare only against the existing port row; if no like-for-like relation
   exists, record the boundary as unevaluable and leave source unchanged.
