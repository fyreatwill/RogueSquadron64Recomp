# NEXT work unit (s2621) — obtain the missing M5 contract mapping

HYPOTHESIS-ID: m5-destub-contract-edge

## Single work unit

Acquire the missing independent contract mapping for retail PC `0x800078EC`
and the secondary-span writers. It must identify the port-side writer or CPU
MORT publication boundary, destination span, legitimate payload polarity, and
ordering relative to image completion and PCM consumption. Do not repeat the
title-zero census and do not change runtime behavior.

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
remains unproven. Existing evidence selects `H-Unproven`.

## Exact checks

1. Obtain independent oracle/decomp attribution of the retail writer PC(s) to
   the logical audio publication contract; whole-RDRAM and title controls must
   be present before any narrow retail null is interpreted.
2. Search the companion/source/fixup tree for the corresponding port writer or
   CPU MORT output boundary and record writer identity, destination, value
   legitimacy, phase, and producer-before-consumer ordering for every candidate.
3. If one edge is complete, write its exact rollback and one-build A/B recipe
   here. If no mapping is complete, remain blocked; do not build or run a
   guessed edge.

## Expected outcomes

- Legitimate image edge: record it and queue one validation soak; do not add
  broad writeback or remapping.
- CPU MORT edge: move the next unit to the named CPU-side boundary.
- No complete edge: remain blocked on the missing independent ground truth; do
  not repeat the same null experiment. The single refuting experiment is an
  oracle watch/companion attribution tying `0x800078EC` to a named port writer
  or CPU publication destination with valid payload ordering.
