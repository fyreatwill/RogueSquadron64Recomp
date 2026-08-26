# NEXT work unit (s2392) — narrow the retail payload witness to exact stage windows

HYPOTHESIS-ID: m5-image-stage-nonzero-contract

## Work unit

Perform one ground-truth-first oracle audit using representative exact
destination/length windows from the retained target rows (at least one title
`0x300`, one title `0x198`, and one hangar `0x300`/`0x198` window). Keep the
whole-RDRAM positive control first, and use phase-gated writer histograms plus
post-value summaries for each exact watch. Compare retail final bytes/nonzero
counts and writer PCs against the port rows' destination, length, FNV, and
`stage_nz`.
Do not change task data, audio, gate, fallback, dispatch, VI, or output
behavior. If the oracle cannot reach the target phase or expose bytes, record
that discriminator failure and stop without a port instrument.

## Competing hypotheses and discriminator

- H-StageNonzeroLegitimate: stage payloads are legitimately zero and the image
  matcher must reject them; reporter-only associations are expected.
- H-StageNonzeroLoggingArtifact: the stage logger records the wrong hash/byte
  region, so a positive-control recomputation from the same retained bytes
  makes `stage_nz` nonzero.
- H-StageNonzeroPcmMismatch: stage and PCM records refer to different payload
  representations; the exact destination/length/hash join fails while a
  source-region or task-range join explains the zero.
- H-StageCaptureInvalid: the oracle loses its whole-RDRAM or title/hangar
  controls.

The discriminator is one table for the selected windows: oracle phase,
destination/length, writer PCs, final nonzero/FNV, and matching port fields.
Exact retail zeros select H-StageNonzeroLegitimate; exact retail nonzero bytes
with a port/logger zero select H-StageNonzeroLoggingArtifact; a different
exact source window that matches the port stage selects
H-StageNonzeroPcmMismatch; failed controls select H-StageCaptureInvalid.

## Exact commands / controls

    rg -n -C 20 'rs64_audio_join_image|audtask-image-stage-row|stage_nz' src lib scratch tools/oracle
    sed -n '1,220p' tools/oracle/README.md
    # Then run one oracle recipe with exact windows, its whole-RDRAM positive
    # control, title/hangar phase trace, and post-value summaries.

Expected controls are a whole-RDRAM oracle watch hit, both target phase
origins if reachable, and a bounded stage-byte read/watch. A null without
those controls is inconclusive. No port build is authorized unless the
ground-truth audit identifies a specific logger-region ambiguity.
