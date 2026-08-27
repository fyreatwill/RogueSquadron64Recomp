# NEXT work unit (s2662) — map the M5 output publication boundary

HYPOTHESIS-ID: m5-output-publication-boundary

## Work unit

Run one ground-truth-first, phase-gated M5 mapping capture using the existing
retail oracle and port image arm. Correlate the retail writer PCs for the
`0x166450:0x169450` and `0x1798B0:0x179A48` spans with the port's image DMA
ranges, PCM source/consumer rows, task ordinal, and completion ordering. Do
not change output fields, writeback, remap, gates, waits, or generated code.

## Competing hypotheses and discriminator

- `H-RetailWriterIsImageEdge`: a retail writer destination/payload maps to a
  nonzero port image DMA span before PCM consumption.
- `H-RetailWriterIsCpuMortEdge`: the retail writer maps to a CPU-side MORT
  publication/descriptor edge, independent of image DMA completion.
- `H-DifferentContract`: neither span maps to the observed image or MORT rows;
  the port-side contract remains unidentified.

The discriminator is one phase-keyed table with retail writer PC, physical
destination, value polarity, port task ordinal, image DMA destination and
payload nonzero count, MORT descriptor class, PCM source/consumer ordinal, and
ordering relative to image completion. A whole-RDRAM oracle control, retail
title/hangar transitions, and port image positive controls must all pass. A
writer count or destination overlap without payload and ordering is
unevaluable.

## Exact commands

1. Reuse the established oracle recipe and its whole-RDRAM positive control;
   inspect the existing phase-gated driver before editing any instrumentation:
   `sed -n '1,220p' scratch/agent/run_s2335_m5_descriptor_filter_boundary.sh`.
2. Create one self-contained capture recipe under
   `scratch/agent/soak_queue/` only after confirming the existing probes cover
   all table columns; otherwise add the complete table in one build through
   the fixup/runtime instrumentation path.
3. Run the oracle and image arm from `build/`, with
   `PROBE_PHASE_WIDTH=1 PROBE_KEYS_FROM_PHASE=1`, and terminate the process
   group with SIGKILL. Collect the table and positive-control summary.
4. Select exactly one hypothesis from the table. Do not land behavior unless
   `H-RetailWriterIsImageEdge` or `H-RetailWriterIsCpuMortEdge` names a
   legitimate writer, payload, destination, and ordering.

## Expected outcomes

- A nonzero, ordered image-DMA match selects `H-RetailWriterIsImageEdge` and
  identifies the next contract edge without changing it.
- An independent MORT descriptor/publication match selects
  `H-RetailWriterIsCpuMortEdge` and keeps RSP task dispatch unchanged.
- Passing controls with no complete mapping selects `H-DifferentContract`;
  leave all behavior unchanged and pivot only after documenting the missing
  edge.
