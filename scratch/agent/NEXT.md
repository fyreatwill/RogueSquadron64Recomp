# NEXT work unit — trace the upstream producer feeding zero PCM RSP-DMA input

HYPOTHESIS-ID: m5-port-zero-pcm-source

Do exactly one bounded M5 source census next iteration. Do not modify output,
waits, slots, status handling, consumer dispatch, or PCM writeback.

Competing hypotheses:

- H-PortRSPSourceZero: the upstream producer feeding the active RSP input
  DMEM is absent or writes zero.
- H-PortRSPTransformZero: source DMEM is nonzero, but the active transform
  emits zero; currently unevaluable.
- H-PortDMADestinationMismatch: the joined DMA targets a different source
  than the consumer; currently refuted for joined stage-2/3 rows.

Discriminating measurement:

Enumerate every upstream write/DMA that populates the stage-2/3 RSP input
DMEM windows (0x6F0 and 0xCB0), record phase and audio-task ordinal, and join
each producer to the existing stage/DMA row in one instrument and one run.
No producer or only zero-valued writes selects H-PortRSPSourceZero. A nonzero
producer followed by zero at the stage call selects H-PortRSPTransformZero. A
producer targeting a different DMEM window reopens H-PortDMADestinationMismatch.

Before building, ask ground truth from the retail oracle for the physical
source-DMEM/input spans and verify the existing port DMEM/DMA hooks. Then
batch the full producer census into the regeneration-surviving instrumentation
and follow:

make_elf.py -> N64Recomp -> fixup_game_funcs.py -> CMake
cmake --build build --config Debug --target RogueSquadron64Recomp

Run from build/ with the ROM present, phase-gated on VI transitions. Require
same-run positive controls for phase, audio-task/ABI, PCM, image-stage/DMA,
title 1024, and hangar 512. Kill with SIGKILL and capture output to a
non-dot-prefixed path. Record the result in a new scratch evidence file and
PORTING-STATE.md, then update CURRENT-TRUTH and commit.

