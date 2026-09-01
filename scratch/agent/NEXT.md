# NEXT work unit — attribute the zero source DMA for image-task DMEM

HYPOTHESIS-ID: m5-output-source-writer

Session 3540 completed the title-phase source-window ordering probe. Window 2
became nonzero, then zero; a post-copy DMA from RDRAM `0x178C80` produced the
zero state and a later `0x1E2FC0` DMA refilled it. Window 3 stayed zero. The
run reached title 1024 but not hangar 512. Retail independently passed its
whole-RDRAM control and wrote nonzero bytes in the corresponding ranges. See
`docs/M5-S3540-SOURCE-WINDOWS.md`.

Next unit: attribute the writer that makes RDRAM `0x178C80` zero before the
source DMA. Join phase-qualified port writes to the selected source-window
event and arm a retail physical watch on the same range, with the whole-RDRAM
control in the same oracle run.

Competing hypotheses and discriminator:

- `H-RdramWriterAbsent`: no port or retail writer reaches `0x178C80`.
- `H-RdramWriterPort`: the port has a writer at the selected predecessor and
  retail does not; select a route-specific producer contract gap.
- `H-RdramWriterParity`: both sides have the same legitimate writer class and
  ordering; move the boundary to source-DMA input or task sequencing.
- `H-CaptureInvalid`: any positive control, target phase, or event join fails.

The one-run table must contain phase, source range, writer PC/kind, event
ordinal, value hashes, and nearest source-DMA/stage/completion/PCM ordinals.
Missing controls or phase rows select `H-CaptureInvalid`; a port-only writer
selects `H-RdramWriterPort`; matching writer class and ordering selects
`H-RdramWriterParity`; absent writers on both sides select
`H-RdramWriterAbsent`.

Exact commands:

    cmake --build build -j8
    # first run the retail oracle with whole-RDRAM control plus a watch on
    # 0x178C80:0x178D80, then run one real-audio LLE/spin-yield/autopilot capture from build/ with
    # ROGUESQ_LOG_M5_SOURCE_WRITER=1, ROGUESQ_LOG_M5_RSP_SOURCE=1,
    # ROGUESQ_LOG_M5_STAGE_CALLS=1, ROGUESQ_LOG_M5_STAGE_BYTES=1,
    # ROGUESQ_LOG_PCM_BOUNDARY=1, ROGUESQ_LOG_M5_PCM_WRITER=1,
    # ROGUESQ_LOG_M5_TASK_CONTRACT=1.

Do not change audio, PCM, or output state.
