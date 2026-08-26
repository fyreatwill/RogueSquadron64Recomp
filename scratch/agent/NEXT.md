# NEXT work unit (s2390) — validate the image-stage nonzero predicate

HYPOTHESIS-ID: m5-image-stage-nonzero-contract

## Work unit

Perform one ground-truth-first, analysis-only audit of the image-stage
`stage_nz != 0` admission predicate. Use the retained s2387 logs and source
definitions; do not change task data, audio, gate, fallback, dispatch, VI, or
output behavior. Determine whether the zero `stage_nz` values are a real
stage/output contract, a logging/hash artifact, or a mismatch between the
stage record and the PCM record.

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

The discriminator is a single table for all four arms and both target phases:
recompute nonzero from the logged stage/hash inputs, compare stage and PCM
destination/length/FNV/nonzero fields, and report exact task-range joins.
Legitimate zeros with exact stage/DMA joins select H-StageNonzeroLegitimate;
recomputed positive values select H-StageNonzeroLoggingArtifact; only a
payload-representation mismatch selects H-StageNonzeroPcmMismatch; failed
controls select H-StageCaptureInvalid.

## Exact commands / controls

    rg -n -C 12 'audio_image_match|audtask-image-stage-row' lib/N64ModernRuntime/librecomp/src/rsp.cpp
    python3 scratch/agent/s2390_audit_stage_nonzero.py scratch/agent/s2387_m5_incomplete_reporter

Expected controls are title `1024`, hangar `512`, `controls=1` for all four
arms, and zero crash/abort markers. No game run or build is needed unless the
retained logs lack the positive stage/DMA fields required by the table.
