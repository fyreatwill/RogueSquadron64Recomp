# NEXT work unit (s2387) — M5 incomplete reporter semantics

HYPOTHESIS-ID: m5-incomplete-task-reporter

## Work unit

Extend the corrected phase/event reporter reducer to classify only image-stage
candidates whose containing raw `[audtask-join]` has `complete=0`. Preserve the
same-build stub/image × c88=0/1 arms and all existing controls. Emit one
bounded table with task `source_matches`, `consumer_matches`,
`source_before_consumer`, `pcm_after_task`, `consumer_after_task`, DMA count,
and stage/task event ordering. This is analysis only: no task-data, audio,
gate, fallback, dispatch, VI, or output behavior change.

## Competing hypotheses and discriminating measurement

- H-IncompleteNoConsumer: incomplete reporter rows have a source match but no
  consumer match; the missing consumer is the remaining closure edge.
- H-IncompleteNoSource: incomplete rows have a consumer match but no source;
  the source publication edge is missing.
- H-IncompleteOrdering: both matches exist, but the reporter remains
  incomplete because source/consumer ordering or task-boundary ordering fails.
- H-IncompleteJoinArtifact: the incomplete classification disappears when the
  stage is joined to the containing raw reporter interval, while route and
  positive controls still pass.

The discriminator is the complete table of incomplete reporter-candidate rows,
not a count-only summary: each row must show the raw task ordinal, interval,
DMA count, complete bit, source/consumer presence, ordering bits, and stage
event. H-IncompleteNoConsumer, H-IncompleteNoSource, or H-IncompleteOrdering
is selected by the dominant mutually exclusive pattern; H-IncompleteJoinArtifact
is selected only if no valid containing interval remains. Failed controls select
H-IncompleteCaptureInvalid.

## Exact commands / controls

    rg -n -C 6 'audio_join_report_locked|audtask-join|source_before_consumer|pcm_after_task' lib/N64ModernRuntime/librecomp/src/rsp.cpp
    rg -n -C 5 'reporter-candidate-table|reporter_candidate' scratch/agent/run_s2345_m5_c88_downstream_ordinal_join.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s2345_m5_c88_downstream_ordinal_join.sh s2387_m5_incomplete_reporter

Expected controls are a successful build, title `1024`, hangar `512`, all four
arms retained, and zero crash/abort markers. If any control fails, select
H-IncompleteCaptureInvalid and do not interpret incomplete rows.
