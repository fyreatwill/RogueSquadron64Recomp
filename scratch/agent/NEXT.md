# NEXT work unit (s2389) — audit reporter range matching against image-stage matching

HYPOTHESIS-ID: m5-reporter-range-matching

## Work unit

Build one bounded reducer over the retained s2387 raw logs. For every image
stage candidate, compare the exact task reporter range(s) selected by
`audio_join_match_task_locked` with the image-stage source/consumer matches.
Report task ordinal, stage ordinal/row, DMA event, DMEM/guest/length/hash,
reporter range index, source/consumer indices, and whether the two matchers
select the same range. Analysis only: no task-data, audio, gate, fallback,
dispatch, VI, or output behavior change.

## Competing hypotheses and discriminating measurement

- H-RangeMatcherAgreement: reporter and image-stage matchers select the same
  DMA range; incomplete rows are genuinely unmatched task ranges.
- H-RangeMatcherConflict: both matchers find a source/consumer edge but select
  different ranges, so the apparent stage-only classification is a reducer
  association artifact.
- H-RangeMatcherMultiplicity: duplicate or reused PCM records make greedy
  matching order-dependent; a stable one-to-one assignment changes the
  source/consumer classification.
- H-RangeCaptureInvalid: any arm loses title/hangar controls or the positive
  image-stage/reporter associations.

The discriminator is one range-level table covering all four arms and both
target phases. Agreement on every retained incomplete row selects
H-RangeMatcherAgreement; any same-key differing range selects
H-RangeMatcherConflict; a change only after stable one-to-one reassignment
selects H-RangeMatcherMultiplicity; failed controls select
H-RangeCaptureInvalid.

## Exact commands / controls

    sed -n '586,626p' lib/N64ModernRuntime/librecomp/src/rsp.cpp
    rg -n -C 10 'audio_join_match\(|audio_image_match\(' lib/N64ModernRuntime/librecomp/src/rsp.cpp
    env REUSE_LOGS=1 zsh scratch/agent/run_s2345_m5_c88_downstream_ordinal_join.sh s2387_m5_incomplete_reporter

Use the retained logs only; no new binary or game run is needed unless the
range-level reducer cannot validate all four controls. Expected controls are
title `1024`, hangar `512`, and `controls=1` for stub_c0, stub_c1, image_c0,
and image_c1, with zero crash/abort markers.
