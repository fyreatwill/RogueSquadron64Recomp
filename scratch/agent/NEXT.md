# NEXT work unit — locate the exact zeroing edge in image-task DMEM

HYPOTHESIS-ID: m5-output-source-writer

Session 3539 extended the source census to vector stores. The real-audio port
reached title and hangar, logged vector writes in both source-window classes,
and showed nonzero broad-span DMEM contents during the producer sequence; the
later stage-2 source snapshot and PCM output remained zero. Retail independently
passed its whole-RDRAM control and wrote nonzero bytes in both watched ranges.
See `docs/M5-S3539-SOURCE-WRITER.md`.

Next unit: refine the existing source census to hash each source window
separately after every vector/scalar store and after every RSP DMA read. Join
each row to the image-stage, source-DMA, completion, PCM-source, and
PCM-consumer event ordinals. Keep the retail PCs as attribution anchors only.

Competing hypotheses and discriminator:

- `H-SourceWindowAbsent`: one individual source window has no producer; select
  a window with no store/read row before its stage snapshot.
- `H-SourceWindowZeroed`: a producer/read reaches a window with zero bytes;
  select that producer event and its zero post-hash.
- `H-SourceWindowOverwritten`: a window becomes nonzero, then a later DMA or
  vector/scalar store makes it zero; select the ordered nonzero-to-zero pair.
- `H-CaptureInvalid`: any positive control, target phase, or event join fails.

The one-run table must contain phase, window, event ordinal, writer kind,
DMEM/RDRAM range, pre/post FNV/nonzero counts, and nearest stage/completion/
PCM ordinals. A missing row selects `H-SourceWindowAbsent`; zero at the first
producer selects `H-SourceWindowZeroed`; nonzero followed by zero selects
`H-SourceWindowOverwritten`; failed controls select `H-CaptureInvalid`.

Exact commands:

    cmake --build build -j8
    # run one real-audio LLE/spin-yield/autopilot capture from build/ with
    # ROGUESQ_LOG_M5_SOURCE_WRITER=1, ROGUESQ_LOG_M5_RSP_SOURCE=1,
    # ROGUESQ_LOG_M5_STAGE_CALLS=1, ROGUESQ_LOG_M5_STAGE_BYTES=1,
    # ROGUESQ_LOG_PCM_BOUNDARY=1, ROGUESQ_LOG_M5_PCM_WRITER=1,
    # ROGUESQ_LOG_M5_TASK_CONTRACT=1, and the independent retail controls.

Do not change audio, PCM, or output state.
