# NEXT work unit (s2425) — independently attribute the observed M5 guest writer

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

Use the retail oracle to phase-gate the two observed candidate PCs
`0x80015BC8` and `0x8000F3A0`, with the existing positive controls, and dump
their argument/field context in title and hangar. Compare those rows against
the fixed s2424 port rows and the image DMA identity. This is observation-only:
do not change task data, output ranges, gates, guards, dispatch, or defaults.

## Competing hypotheses and discriminator

- H-RetailSameWriter: retail `0x80015BC8` has the same candidate address and
  structure context as the port title writer, supporting a legitimate shared
  writer identity.
- H-RetailDifferentRole: retail execution reaches the PC but its fields/range
  differ from the port row, so the port row is not the retail consumer.
- H-RetailNoExecution: the PC has no phase-gated retail execution hits despite
  valid controls; the prior attribution is not a usable writer witness.
- H-ControlsInvalid: a whole-RDRAM, title, hangar, or selected-PC control fails.

The discriminator is the single oracle phase/PC field table joined to the
existing port tuple `(pc, phys, ordinal, row, task_data, dma_dest)`. Matching
PC plus candidate address/field context selects H-RetailSameWriter; a valid
different context selects H-RetailDifferentRole; valid controls with zero PC
hits select H-RetailNoExecution; any missing positive control selects
H-ControlsInvalid.

## Exact commands

1. Before adding instrumentation, run the existing oracle recipe with
   `--watch-write 0x0:0x800000`, exact title/hangar windows, and
   `--watch-pc 0x80015BC8,0x8000F3A0`, using Rice and the verified eleven-Start
   schedule. Require the whole-RDRAM positive-control threshold plus both VI
   phases before interpreting PC rows.
2. If the existing oracle field output is sufficient, add no port code. If a
   bounded field table is needed, add it to the oracle only, then run once.
3. Compare against `scratch/agent/s2424_m5_guest_writer_fixed/`; no behavior
   change is authorized.
