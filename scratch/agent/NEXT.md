# NEXT work unit (s2388) — audit raw reporter completion predicate

HYPOTHESIS-ID: m5-reporter-completion-predicate

## Work unit

Audit the raw `audio_join_report_locked` completion predicate against the
s2387 incomplete-row table. Trace how `sources`, `consumers`, `complete`, and
the ordering flags are accumulated across task ranges, then run the bounded
reducer on the retained s2387 logs with one table that distinguishes
stage-only, source-only, consumer-only, and both-match rows by task ordinal
and range count. Analysis only: no task-data, audio, gate, fallback,
dispatch, VI, or output behavior change.

## Competing hypotheses and discriminating measurement

- H-PredicateRequiresSameRange: `complete` requires source and consumer on one
  joined DMA range, so aggregate source/consumer counts can be nonzero while
  incomplete stage-only rows are expected.
- H-PredicateGlobalCounts: `complete` is based on task-global source and
  consumer totals, so incomplete rows indicate a missing aggregate edge.
- H-PredicateOrderingOnly: both sides are joined, but a task/range ordering
  condition clears completion.
- H-PredicateReducerMismatch: the source/consumer fields in the raw reporter
  do not describe the same ranges selected by the stage reducer.

The discriminator is a source-level predicate table plus the s2387 row table:
for every incomplete candidate, show task ordinal, range count, each range's
source/consumer indices, aggregate counts, same-range-both bit, and ordering
flags. Same-range-both with complete=0 selects H-PredicateOrderingOnly;
nonzero aggregate counts with no same-range-both selects
H-PredicateRequiresSameRange; disagreement with the reducer selects
H-PredicateReducerMismatch. Failed route/phase controls select
H-PredicateCaptureInvalid.

## Exact commands / controls

    sed -n '507,580p' lib/N64ModernRuntime/librecomp/src/rsp.cpp
    rg -n -C 8 'AudioJoinRange|source_pcm|consumer_pcm|complete = true' lib/N64ModernRuntime/librecomp/src/rsp.cpp
    env REUSE_LOGS=1 zsh scratch/agent/run_s2345_m5_c88_downstream_ordinal_join.sh s2387_m5_incomplete_reporter

Expected controls are the retained s2387 four-arm capture, title `1024`,
hangar `512`, all four `controls=1`, and zero crash/abort markers. No new
binary or game run is needed unless the retained logs fail validation.
