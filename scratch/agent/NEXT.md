# Next: join input DMA payloads to task ownership

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3672 exposed the opposite direction. The qualified capture passed all
controls and produced 1,024 input-span rows plus 512 writeback rows. Title
input chunks had nonzero payloads (`nz=112/216`), while hangar input chunks
were zero; source and post-DMEM hashes matched.

Competing hypotheses:

- H-SameTaskInput: the new input-DMA event lies in the same route/task ordinal
  as the matching audio task row and its source object.
- H-InterleavedTaskInput: input-DMA ordinals map to a different or alternating
  task object than the immediately reported target task.
- H-HangarZeroProducer: hangar's zero input is already present at the input
  DMA source and belongs to a distinct producer/object state.
- H-HangarZeroTransform: hangar input is nonzero before the DMA but becomes
  zero only in the audio-task staging path.

The prior capture established `H-InputDmaObserved` and refuted
`H-OnlyWritebackObserved`; those are closed for this source-span hook.

Discriminating measurement: in one validated real-audio capture, join each
`m5-source-range-reader` row by route ordinal/event to the nearest
`audtask-abi`/`audtask-dma-range` row, retaining task data pointer, source
object, direction, source/post-DMEM hashes, and phase. Matching ordinals and
object select H-SameTaskInput; alternate objects select H-InterleavedTaskInput.
For hangar rows, source_nz=0 before staging selects H-HangarZeroProducer;
nonzero source with zero staged data selects H-HangarZeroTransform. Require
whole-RDRAM, title, hangar, RSP-source-hook, and type-2 controls; a missing
control invalidates the capture.

Before building, read the existing source/task join code and the relevant env
catalog. Build one instrumentation arm and run one 55-second capture from
`build/`. No guest-state rewrite or mitigation is in scope.
