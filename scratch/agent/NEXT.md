# NEXT work unit (s2391) — obtain a payload-level witness for image-stage nonzero

HYPOTHESIS-ID: m5-image-stage-nonzero-contract

## Work unit

Perform one ground-truth-first payload-level audit of the image-stage
`stage_nz != 0` admission predicate. First use the independent retail oracle
with its whole-RDRAM positive control and a phase-gated watch/read of the
stage destination/length fields identified by the retained image rows; then
compare observed bytes/nonzero counts with the port logger's stage fields.
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
- H-StageCaptureInvalid: any retained arm loses title/hangar or positive
  stage/DMA controls.

The discriminator is one table for both retail target phases and matching port
target rows: oracle byte/nonzero witness, port byte/nonzero witness,
destination/length/hash, and exact task-range join. Legitimate zero bytes
select H-StageNonzeroLegitimate; positive oracle/port bytes with a logger zero
select H-StageNonzeroLoggingArtifact; different but valid byte regions select
H-StageNonzeroPcmMismatch; failed oracle controls select
H-StageCaptureInvalid.

## Exact commands / controls

    rg -n -C 20 'rs64_audio_join_image|audtask-image-stage-row|stage_nz' src lib scratch tools/oracle
    sed -n '1,220p' tools/oracle/README.md
    # Then run the oracle recipe selected by the source audit, with its
    # whole-RDRAM positive control and target-phase gate.

Expected controls are a whole-RDRAM oracle watch hit, both target phase
origins if reachable, and a bounded stage-byte read/watch. A null without
those controls is inconclusive. No port build is authorized unless the
ground-truth audit identifies a specific logger-region ambiguity.
