# NEXT work unit (s2423) — phase-key the port consumer-writer table

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

Add one observation-only, bounded port table at the existing audio/image
consumer boundary. Record every phase-gated write or consumer event that can
touch the retail-selected candidate ranges, joined to image DMA ordinal/row,
task data pointer, and SP return. Keep the image opt-in and do not change task
data, output ranges, gates, guards, dispatch, or defaults.

## Competing hypotheses and discriminator

- H-MissingImageConsumer: valid image DMA/SP rows have no later port writer or
  consumer event for the candidate range.
- H-LegitimateConsumerWriter: a port writer/event joins the image row with the
  same range and ordering as a retail candidate writer.
- H-SharedConsumerWriter: a port writer exists, but only a phase transition or
  task-field key joins it to the image row.
- H-PortTableInvalid: the positive controls or image route fail, so a null is
  uninterpretable.

The discriminating measurement is one phase-scoped row per candidate range
with port event/PC, value/length, image ordinal/row, data pointer, DMA
destination, break/SP return, and PCM/slot controls. A same-identity matching
range/order selects H-LegitimateConsumerWriter; only a phase/task-field join
selects H-SharedConsumerWriter; valid controls with no event select
H-MissingImageConsumer. Missing controls select H-PortTableInvalid.

## Exact commands

1. Before instrumentation, map the existing image-stage/DMA and consumer
   logging sites:
   `rg -n 'audtask-image-stage|audtask-dma-range|slot-sb|pcm-boundary|filter-voice' src lib tools`
   and identify the narrowest existing write/consumer boundary. Do not add a
   counter until the table fields above can all be populated.
2. Build one instrumented target:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run the independent oracle control and the two-arm driver in one capture,
   preserving the whole-RDRAM/title/hangar gate and SIGKILL cleanup. Reuse the
   candidate ranges `0x167000:0x169B00`, `0x179800:0x179B00`, and
   `0x18FC00:0x18FD00`:
   `zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh s2423_m5_port_writer`
4. Summarize only phase-gated rows in
   `scratch/agent/s2423_m5_port_writer/`; leave behavior unchanged.

Expected outcomes: both port arms and the independent controls must reach
title and hangar. A matching port writer selects the legitimate/shared arm;
valid controls with no event preserve H-MissingImageConsumer provisionally.
