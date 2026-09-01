# NEXT work unit — attribute the port 0x800078EC zero-fill origin

HYPOTHESIS-ID: m5-output-source-writer

Session 3541 completed the corrected source-RDRAM writer probe. Retail passed
the whole-RDRAM control, reached title and hangar, and showed a distinct
multi-PC writer family with a nonzero final snapshot. The port reached both
target phases and recorded 768 span-writer rows; the selected `0x178C80` span
was written as zero bytes by one port writer PC, `0x800078EC`. Candidate-store
and memset hooks were silent, while downstream image-stage and join controls
remained live. See `docs/M5-S3541-SOURCE-RDRAM-WRITER.md`.

Next unit: identify the port-side writeback/DMA path represented by writer PC
`0x800078EC`, including its source address, length, and payload hash at the
same phase-qualified zero write. Use static callsite enumeration plus one
same-build capture with the existing positive control and downstream joins.

Competing hypotheses and discriminator:

- `H-WritebackOrigin`: `0x800078EC` maps to a concrete port writeback/DMA
  source whose zero payload explains the selected RDRAM write.
- `H-WriterHookMismatch`: the hook's PC/address contract is not the actual
  source of the zero write; select a corrected attribution instrument.
- `H-WritebackUnknown`: the writer is real but its source path remains
  unresolved after the static census and capture.
- `H-CaptureInvalid`: any positive control, target phase, or event join fails.

The one-run table must contain phase, writer PC, port callsite/source kind,
source address, length, payload hash/nonzero count, and nearest source-DMA,
stage, completion, and PCM ordinals. Missing controls or phase rows select
`H-CaptureInvalid`; a concrete source path with matching zero payload selects
`H-WritebackOrigin`; a PC/address mismatch selects `H-WriterHookMismatch`;
an unresolved but valid writer selects `H-WritebackUnknown`.

Exact commands:

    cmake --build build -j8
    # run one real-audio LLE/spin-yield/autopilot capture from build/ with
    # ROGUESQ_LOG_M5_SOURCE_WRITER=1, ROGUESQ_LOG_M5_FIELD348_WRITER=1,
    # ROGUESQ_LOG_M5_FIELD348_CANDIDATES=1, ROGUESQ_LOG_M5_FIELD348_MEMSET=1,
    # ROGUESQ_LOG_M5_RSP_SOURCE=1,
    # ROGUESQ_LOG_M5_STAGE_CALLS=1, ROGUESQ_LOG_M5_STAGE_BYTES=1,
    # ROGUESQ_LOG_PCM_BOUNDARY=1, ROGUESQ_LOG_M5_PCM_WRITER=1,
    # ROGUESQ_LOG_M5_TASK_CONTRACT=1.

Do not change audio, PCM, or output state.
