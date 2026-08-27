# NEXT work unit (s2620) — select the first proven M5 contract edge

HYPOTHESIS-ID: m5-destub-contract-edge

## Single work unit

Perform one bounded Step 3 contract audit from `docs/M5-AUDIO-PLAN.md`: use
the collected retail writer spans and generated Factor 5 image-stage/DMA rows
to select exactly one proven output/publication edge that can be changed
safely. This is a selection/design unit, not another title-zero runtime
census. If no edge has a named writer, legitimate value, destination, and
ordering, stop without a behavior change and mark the item blocked on that
missing contract fact rather than inventing writeback.

## Competing hypotheses and discriminator

- `H-ImageOutputEdge`: the Factor 5 image has a legitimate, named output
  destination/writeback edge missing from the port contract.
- `H-CPU-MORT-Edge`: title PCM is owned by the CPU MORT path, so image-task
  writeback would be the wrong boundary.
- `H-Unproven`: existing rows do not establish a legitimate edge; no behavior
  change is authorized.

The discriminator is one evidence table mapping each candidate to retail
writer PC, port writer/consumer, physical destination span, payload polarity,
phase, and ordering relative to image completion and PCM consumer. One
complete legitimate mapping selects that edge; an image-stage-only candidate
remains unproven.

## Exact checks

1. Read the existing oracle artifact and `docs/M5-AUDIO-PLAN.md`; search the
   generated/fixup image-stage, DMA, MORT, and PCM boundary callsites as one
   candidate table. Do not add an instrument until the whole-RDRAM control and
   retail title writer rows are present.
2. Record writer identity, destination, value legitimacy, phase, and
   producer-before-consumer ordering for every candidate. A missing field is
   `H-Unproven` and must not be implemented.
3. If one edge is complete, write its exact rollback and one-build A/B recipe
   here for the next iteration. Do not build or run a guessed edge in this
   unit.

## Expected outcomes

- Legitimate image edge: record it and queue one validation soak; do not add
  broad writeback or remapping.
- CPU MORT edge: move the next unit to the named CPU-side boundary.
- No complete edge: record the evidence table and ask for the missing ground
  truth; do not repeat the same null experiment.
