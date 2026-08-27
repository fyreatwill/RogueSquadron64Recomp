# NEXT work unit (s2619) — establish the title PCM positive control

HYPOTHESIS-ID: m5-title-publication-boundary

## Single work unit

Perform one bounded M5 title-publication investigation using the existing
phase-gated image/silent pair and the already-qualified controls. Do not
revisit the hangar indexed writer until the image arm has a same-run nonzero
title PCM control. Add no output remap, writeback, gate bypass, or forced slot
state.

## Competing hypotheses and discriminator

- `H-TitlePublicationMissing`: title image-stage output or its PCM
  publication edge remains zero while the silent control remains separated.
- `H-TitlePhaseMisjoin`: title PCM exists, but current phase/origin or source /
  consumer sampling fails to join it.
- `H-TitleWriterEdge`: a legitimate nonzero title writer/source edge is found
  and orders before the exact PCM consumer span.

The discriminator is one phase-gated title table joining image-stage/DMA
payload, source and consumer span, nonzero count, writer PC/destination/value,
C88, and arm. A nonzero title source/consumer join selects
`H-TitleWriterEdge`; a nonzero row that fails the phase/span join selects
`H-TitlePhaseMisjoin`; title-zero image output with the silent separation
selects `H-TitlePublicationMissing`.

## Exact checks

1. Ask the retail oracle for the already-established title writer/destination
   ground truth before adding any new port probe. Then, in one rebuilt binary,
   run image and silent arms with `ROGUESQ_M5_C88_VALUE=0`,
   `PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, and
   `PROBE_LEAVE_OK=1`; batch the existing stage, DMA, task, writer, and PCM
   join logs. Compare title rows only; retain hangar rows as a secondary
   control.
2. A joined nonzero title row selects `H-TitleWriterEdge`; a nonzero row with
   a failed span/phase join selects `H-TitlePhaseMisjoin`; title-zero image
   output with silent separation selects `H-TitlePublicationMissing` and
   requires a pivot to the M5 de-stubbing plan rather than another identical
   null chase.

## Expected outcomes

- Legitimate hangar edge: record it and queue one validation soak; do not add
  writeback or remapping.
- Non-audio or absent edge: record the joined table and pivot without changing
  behavior.
