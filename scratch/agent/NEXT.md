# NEXT work unit — identify the legitimate writer of the zero staging source range

HYPOTHESIS-ID: m5-image-task-source-range-writer

Session 3565 selected `H-ZeroDmaOrdering`: in a target-valid hangar task,
nonzero DMEM staging was followed by a clear and then zero stage DMAs. The
remaining boundary is the RDRAM source range read by those DMAs.

Before building, use one phase-keyed table with the competing hypotheses and
the single discriminator:

- H-SourceRangeCpuWriter: a guest CPU store or memset writes the source range
  (`0x1797B0`/`0x1798B0`) before the zero DMA.
- H-SourceRangeDmaWriter: an earlier RSP DMEM-to-RDRAM DMA writes the source
  range, with its payload/hash explaining the zero source.
- H-SourceRangeStaleOrUnwritten: neither writer occurs before the zero DMA, so
  the range is stale or never initialized on this route.

The discriminator is a phase/task-ordinal ordering table for every CPU store,
memset, DMEM-to-RDRAM DMA, and image-stage source DMA overlapping the two
source ranges. Each row must include writer kind/PC or DMA source, payload
hash/nonzero count, range, route ordinal, and shared event sequence. A
phase/task-matched CPU/memset writer selects H-SourceRangeCpuWriter; a
DMEM-to-RDRAM writer with matching payload selects H-SourceRangeDmaWriter;
absence of both before the zero read selects H-SourceRangeStaleOrUnwritten.

Run `wc -c < docs/CURRENT-TRUTH.md`, then check the retail oracle prerequisites
before building. Add only the bounded source-range writer/order hooks to the
existing phase-keyed image instrumentation, rebuild once, and run one
standalone image arm from `build/` with the validated real-audio/LLE-solo/
spin-yield/autopilot route. Require title 1024, hangar 512, image-stage,
source-DMA, audio-return, and writer controls before classifying a result.
Use SIGKILL and retain the full log under `scratch/agent/`.
