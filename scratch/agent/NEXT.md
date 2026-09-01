# NEXT work unit — identify the producer before the source-range clear

HYPOTHESIS-ID: m5-output-preclear-producer

Session 3542 closed the `0x800078EC` identity: it is the generated
`rs_memset` byte loop clearing `0x80178C80`/`0x801797B0` for `0x298` bytes.

Do exactly one bounded work unit: enumerate and capture writers to the source
range before each clear. The competing hypotheses and discriminator are:

- `H-PreclearProducer`: a concrete port CPU/RSP/DMA writer populates the range
  before `rs_memset`; the phase-ordered writer and nonzero payload identify it.
- `H-ClearBeforeProducer`: the clear legitimately precedes all producers; the
  first producer is after the clear and the pre-clear snapshot is zero.
- `H-WriterHookMismatch`: the existing writer attribution misses an earlier
  writer; an independent range snapshot/writer control disagrees with the
  `rs_memset` ordering.
- `H-CaptureInvalid`: any positive control, title/hangar phase, or join is
  absent.

The one-run table must include phase, source-range snapshot before clear,
writer kind/PC or DMA source, source/destination/length, payload FNV/nonzero
count, and the `rs_memset` ordinal plus nearest image-stage/source-DMA/join
ordinals. A nonzero pre-clear writer selects `H-PreclearProducer`; zero before
all clears selects `H-ClearBeforeProducer`; an ordering/attribution mismatch
selects `H-WriterHookMismatch`; missing controls select `H-CaptureInvalid`.

Before building, use the existing positive-control and downstream joins. Add
all pre-clear counters in one build and one phase-gated real-audio capture;
do not change audio, PCM, or output state.

Commands:

    cmake --build build -j8
    # Run from build/ with the validated real-audio LLE/spin-yield/autopilot
    # route, ROGUESQ_LOG_M5_WRITER_ENTRY=1, the existing source-writer,
    # field348-writer, RSP-source, stage-call/bytes, PCM, and task controls,
    # plus the new pre-clear snapshot/writer controls.

Do not repeat the closed `0x800078EC` identity probe without pre-clear
ordering. Do not modify audio, PCM, or output state.
