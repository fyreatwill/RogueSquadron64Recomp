# NEXT work unit (s2428) — join the selected retail title writer to the port task row

HYPOTHESIS-ID: m5-image-contract-gap

## Work unit

Run the existing two-arm, phase-gated M5 contract recipe with its observation-only
writer table enabled. Do not change audio behavior, task data, output ranges,
gates, guards, dispatch, or defaults. Retain the exact title writer relation
(`pc=0x80015BC8`, title range `0x169730..0x169B30`) and join it to the port
task-data/ordinal/row table; retain the hangar image-DMA rows for comparison.

## Competing hypotheses and discriminator

- H-PortTitleWriterJoin: title rows from `0x80015BC8` join the exact retail
  range and the same port task-data/ordinal/row identity.
- H-PortTitleWriterRangeOnly: the port exact-range writer rows exist but do not
  join the selected task identity.
- H-PortTitleWriterAbsent: the valid port route has no corresponding CPU writer
  rows; only DMA rows remain.
- H-PortRouteInvalid: either arm misses title or hangar controls.

The discriminator is one phase-keyed table containing exact-range writer PC,
task data, ordinal, row, and arm, plus image-DMA rows. A valid same-row join
selects H-PortTitleWriterJoin; valid controls with no join but writer rows
select H-PortTitleWriterRangeOnly; valid controls with no CPU writer rows
select H-PortTitleWriterAbsent; missing route controls select H-PortRouteInvalid.

## Exact commands

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LOG_M5_PCM_WRITER=1 zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh s2428_m5_title_writer_join

Require the recipe's retail whole-RDRAM/title/hangar controls, both port-arm
title/hangar controls, and positive-control writer rows before interpreting any
null join.
