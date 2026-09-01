# NEXT work unit — identify the source-DMA payload producer

HYPOTHESIS-ID: m5-image-task-source-dma-payload

Session 3569 selected `H-DmemPayloadClearOrStale`: target-valid hangar tasks
performed overlapping vector stores, but the exact DMEM windows remained zero;
no target-phase preclear or static memset fired, and the writeback payload was
zero. The next bounded unit is one phase/task-keyed census of the upstream
RDRAM writer/data source for the zero source DMA.

Competing hypotheses and discriminator:

- H-SourceDmaCpuWriter: CPU writes populate `0x1797B0..0x179930` before the
  source DMA, with a matching phase/task join and nonzero post-write hash.
- H-SourceDmaOtherWriter: an RSP/host DMA or other non-CPU operation supplies
  the source bytes, with a matching writer event and payload transition.
- H-SourceDmaZeroInput: the source DMA reads zero bytes despite no productive
  writer in the preceding task-keyed interval.

The single discriminator is a shared-event table keyed by image-task ordinal
and route row. Reuse the source-range CPU writer, DMA source, and post-value
hooks to record every operation affecting physical
`0x1797B0..0x179930`, including writer PC/operation and post-write hash, then
pair it with that ordinal's RDRAM-to-DMEM source row. A productive CPU row
selects `H-SourceDmaCpuWriter`; another productive operation selects
`H-SourceDmaOtherWriter`; only a live source-DMA control with no preceding
writer and zero payload selects `H-SourceDmaZeroInput`.

Before building, check the retail oracle paths and arm its whole-RDRAM control.
Reuse existing hooks; add only a source-DMA-to-writer ordinal join if current
rows cannot pair the events. Build once if needed, then run one standalone
image arm from `build/` with `ROGUESQ_AUTOPILOT=1`, `ROGUESQ_AUDIO_UCODE=1`,
`ROGUESQ_LOG_ALL=1`, real-audio/LLE-solo/spin-yield, and the phase-gated probe.
Require title 1024, hangar 512, source-DMA, source-range-writer, and positive
writer controls. Use SIGKILL and retain the full log under `scratch/agent/`.
