# NEXT work unit (s2422) — attribute the M5 image consumer writer

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

First run one independent retail-oracle writer-attribution capture for the
candidate title/hangar image-DMA ranges and adjacent task-field range. Only if
the oracle has positive writer hits, run the existing eleven-Start driver once
with both audio arms in the same build and phase-key the port writer table to
the image DMA rows. This is observation-only: do not change task data, output
ranges, gates, guards, dispatch, or the image default.

## Competing hypotheses and discriminator

- H-MissingImageConsumer: the candidate range has no named retail writer and
  no matching port writer at the image task identity.
- H-LegitimateConsumerWriter: retail writes the candidate range from a named
  PC, and the matching port writer is present after image DMA/SP completion.
- H-SharedConsumerWriter: retail/port writers exist, but only a bounded
  phase-transition or task-field key joins them to the image row.
- H-WriterTableInvalid: any oracle whole-RDRAM/title/hangar or port route
  control fails, so the writer null is uninterpretable.

The discriminating measurement is a complete writer row per phase and
candidate range containing retail PC/value/length and port PC/value/length,
joined to task data pointer, ordinal, DMA destination, image break/SP return,
and PCM source/consumer identity. A named writer on both sides selects
H-LegitimateConsumerWriter; only a phase-transition key selects
H-SharedConsumerWriter; valid controls with no named writer selects
H-MissingImageConsumer. Missing controls select H-WriterTableInvalid.

## Exact commands

1. Arm the retail oracle with whole-RDRAM plus candidate ranges from the
   existing image-stage/DMA rows (title `0x168E50`-class and hangar
   `0x168B50`-class spans, plus task-field `0x18FC70`-class bytes), and require
   positive-control threshold, title, and hangar before interpreting a null.
2. If those writer controls pass, build with `cmake --build build --config
   Debug --target RogueSquadron64Recomp`.
3. Run the validated driver, preserving its SIGKILL cleanup and oracle gate:
   `zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh s2422_m5_writer`
   (retain the eleven-Start injector).
4. Summarize only phase-gated rows from the oracle and both arm logs in
   `scratch/agent/s2422_m5_writer/`.

Expected outcomes: oracle whole-RDRAM/title/hangar and both port arms must pass
their route controls. Retail writer hits with matching port writer rows select
the legitimate/shared-writer arm; valid controls with no candidate writer keep
H-MissingImageConsumer provisional. Leave behavior unchanged either way.
