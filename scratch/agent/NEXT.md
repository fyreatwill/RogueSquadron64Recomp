# NEXT work unit — identify the zero DMEM payload producer

HYPOTHESIS-ID: m5-image-task-dmem-payload-writer

Session 3566 selected `H-SourceRangeDmaWriter`: target-valid hangar tasks
write zero DMEM payloads back into `0x1797B0`/`0x1798B0` before the stage reads.
The next bounded unit is one phase/task-keyed census of the DMEM payload
producer immediately before each `0xC30`/`0xCB0` writeback.

Competing hypotheses and discriminator:

- H-DmemPayloadCpuWriter: CPU or memset writes `DMEM[0xC30..0xE48]`'s backing
  input/source state before the RSP task; a matching guest writer and changed
  pre-task payload selects it.
- H-DmemPayloadRdramDma: an RDRAM-to-DMEM DMA supplies the zero payload; its
  source range/hash and event precede the writeback.
- H-DmemPayloadRspStore: RSP scalar/vector stores zero the payload after task
  start; a task-ordinal-matched store event precedes the writeback.
- H-DmemPayloadStale: none of the three writers occurs before the zero
  writeback, so the task begins with stale/uninitialized DMEM.

The single discriminator is a shared-event table keyed by image-task ordinal
and route row. For every writer overlapping `0xC30..0xE48`, record writer kind,
guest PC or DMA source, DMEM range, payload hash/nonzero count, task ordinal,
and event sequence; pair it with the immediately following
`m5-source-range-writer` row. A CPU writer, RDRAM-to-DMEM DMA, or RSP store
with matching zero payload selects its hypothesis; absence of all three before
the writeback selects stale/uninitialized state.

Before building, check `wc -c < docs/CURRENT-TRUTH.md` and the retail oracle
paths. Add only the bounded DMEM payload writer/event hooks to the existing
instrumentation, rebuild once, and run one standalone image arm from `build/`
with the validated real-audio/LLE-solo/spin-yield/autopilot route. Require
title 1024, hangar 512, image-stage, source-DMA, audio-return, and positive
writer controls. Use SIGKILL and retain the full log under `scratch/agent/`.
