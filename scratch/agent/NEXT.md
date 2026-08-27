# NEXT work unit (s2618) — revisit hangar PCM writer/value boundary

HYPOTHESIS-ID: m5-hangar-publication-boundary

## Single work unit

Perform one bounded same-build title/hangar validation of the existing
`0x80094648` indexed writer relation, with C88=`0` and the silent arm as
rollbacks/controls. Add no output remap or writeback. Add a witness only if
the run identifies a legitimate nonzero hangar publication edge.

## Competing hypotheses and discriminator

- `H-HangarWriterLegitimate`: `0x80094648` writes a nonzero hangar PCM value
  to the established destination and orders before the PCM consumer.
- `H-HangarWriterNonPCM`: it writes a nonzero value, but the destination or
  consumer join identifies a non-audio role.
- `H-HangarPublicationGap`: the writer stays zero/absent in hangar while the
  title positive control remains live.

The discriminator is one phase-gated table joining writer PC, destination,
value/nonzero count, C88, image DMA completion, and PCM source/consumer rows
in title and hangar. A nonzero destination- and consumer-matched hangar row
selects `H-HangarWriterLegitimate`; a non-audio use selects
`H-HangarWriterNonPCM`; zero/absent hangar rows with title-positive controls
select `H-HangarPublicationGap`.

## Exact checks

1. Run the existing qualified driver with image and silent arms in one build,
   keeping `PROBE_PHASE_WIDTH=1` and `PROBE_KEYS_FROM_PHASE=1`; enable the
   existing writer, image/DMA, task/event, and PCM join logs.
2. Confirm title PCM is nonzero in the same run before interpreting hangar;
   require image/DMA and PCM positive controls. Ask the retail oracle only if
   the destination relation changes or a new narrow witness is needed.

## Expected outcomes

- Legitimate hangar edge: record it and queue one validation soak; do not add
  writeback or remapping.
- Non-audio or absent edge: record the joined table and pivot without changing
  behavior.
