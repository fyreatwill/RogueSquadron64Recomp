# NEXT work unit — identify the pre-task source initializer

HYPOTHESIS-ID: m5-image-task-source-initializer

Session 3570 selected `H-SourceDmaZeroInput`: target-valid hangar tasks loaded
zero source bytes from `0x1797B0`/`0x1798B0`; all observed source-span writes
were zero DMA writebacks, and the phase-matched `field348-writer` witness at
`0x800078EC` also supplied zero. The next bounded unit is one task-keyed census
of the pre-task initializer/data handoff that leaves the source span empty.

Competing hypotheses and discriminator:

- H-PreTaskCpuInit: a CPU initializer before the image-task ordinal writes the
  source span and its value/hash transitions to the required nonzero content.
- H-PreTaskOtherInit: an earlier task, RSP/host DMA, or route handoff supplies
  the source bytes without a matching CPU initializer.
- H-PreTaskZeroContract: the source span remains zero through the handoff, so
  the image task receives a zero input from an earlier missing or unimplemented
  contract.

The single discriminator is a phase/task-keyed transition table covering the
source span from route preparation through the first image-task source DMA.
Extend the existing source-range writer and field348 hooks only if needed to
record pre-task writer PC/operation, value/hash, and the first subsequent
source-DMA ordinal. A nonzero CPU transition selects `H-PreTaskCpuInit`; a
non-CPU transition selects `H-PreTaskOtherInit`; a live handoff with no
nonzero transition selects `H-PreTaskZeroContract`.

Before building, check the retail oracle paths and arm its whole-RDRAM control.
Reuse existing hooks; add only the pre-task transition join if current rows
cannot pair the `0x800078EC`/source-range events with the first source DMA.
Build once if needed, then run one standalone image arm from `build/` with
`ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'`,
`ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_STUB_MISSING_FUNCS=1`,
`ROGUESQ_LOG_ALL=1`, real-audio/LLE-solo/spin-yield, and the phase-gated probe.
Require title 1024, hangar 512, source-DMA, source-range-writer,
field348-writer, and positive writer controls. Use SIGKILL and retain the full
log under `scratch/agent/`.
