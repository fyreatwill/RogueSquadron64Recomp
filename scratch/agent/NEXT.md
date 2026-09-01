# NEXT work unit — identify the source-range RDRAM producer

HYPOTHESIS-ID: m5-image-task-source-range-producer

Session 3567 selected `H-DmemPayloadRdramDma`: target-valid hangar tasks loaded
zero payloads from `0x1797B0`/`0x1798B0` into DMEM before the stage writebacks,
with no overlapping CPU/RSP DMEM-store row. The next bounded unit is one
phase/task-keyed census of the writer that produces those RDRAM source bytes.

Competing hypotheses and discriminator:

- H-SourceRangeCpuWriter: a guest CPU/memset writer produces the source range
  immediately before the image-task DMA, with a matching guest PC and hash.
- H-SourceRangeOtherDma: another DMA produces the source range; its source,
  destination, and hash precede the image-task source DMA.
- H-SourceRangeStale: neither writer occurs in the task-keyed interval, so the
  zero source range is inherited or initialized elsewhere.

The single discriminator is a shared-event table keyed by image-task ordinal
and route row. For every CPU store or DMA overlapping physical
`0x1797B0..0x179930`, record writer kind, guest PC or DMA source, range/hash,
task ordinal, and event sequence; pair it with the immediately following
`m5-rsp-source` row. A matching CPU writer selects `H-SourceRangeCpuWriter`, a
matching other DMA selects `H-SourceRangeOtherDma`, and absence of both in the
interval selects `H-SourceRangeStale`.

Before building, check `wc -c < docs/CURRENT-TRUTH.md` and the retail oracle
paths. Reuse the existing phase-gated CPU source-span and DMA writer hooks;
add only a task-ordinal join if the current rows cannot pair the events.
Rebuild once if needed, then run one standalone image arm from `build/` with
the validated real-audio/LLE-solo/spin-yield/autopilot route. Require title
1024, hangar 512, image-stage, source-DMA, audio-return, and positive writer
controls. Use SIGKILL and retain the full log under `scratch/agent/`.
