# M5 Session 3571 — pre-task source initializer census

The first standalone attempt was invalid because it omitted the qualified
`ROGUESQ_LLE_FORCE=1` and `ROGUESQ_LLE_UNGATED=1` route variables. The fixed
image arm used the validated autopilot from `build/`, real audio, LLE-solo,
spin-yield, missing-function stubs, `ROGUESQ_LOG_ALL=1`, and the phase gate. It
reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, then was
deliberately stopped with SIGKILL. Phase, RSP-source, DMEM-source, source-range
writer, and field348 writer controls all fired; no crash or abort marker was
present.

In the target handoff, 14 source-DMA rows read `0x1797B0` or `0x1798B0` with
`nz=0`. The source-range table reached its 512-row cap; every sampled hangar
writeback had zero payload and zero post-write nonzero bytes. The phase-matched
source-span CPU witness emitted 244 hangar rows, all from guest PC
`0x800078EC`, all with zero values. No nonzero transition was observed before
the first target source DMA. This selects `H-PreTaskZeroContract` at the
qualified handoff and rules out a productive CPU initializer in the observed
target-phase window.

This does not yet identify the earlier initializer: the existing writer hooks
are phase-gated and therefore cannot witness writes before the target VI
bucket. The next probe must retain the same controls while recording a bounded,
phase-independent source-span transition table and joining its last transition
to the first target source-DMA ordinal.

The retail oracle frontend and ROM were present, but its debugger-enabled core
dylib was absent. Its whole-RDRAM control therefore could not run; all detailed
producer evidence here is single-source port evidence.

ORIGIN: diagnostic-only source handoff census. No output, PCM, task, DMA, or
source state was rewritten.
