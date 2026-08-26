# NEXT work unit (s2386) — M5 task-reporter record boundary

HYPOTHESIS-ID: m5-task-output-gap

## Work unit

Audit the task reporter that emits `[audtask-join]` after s2385 found direct
image completion callbacks but no task `complete` or PCM source/consumer
closure. First use the existing retail oracle whole-RDRAM and target-phase
controls; then add one phase-scoped, behavior-neutral reporter table to the
existing four-arm driver. For each image-stage candidate, join the containing
`[audtask-join]` record by phase and event interval and retain task ordinal,
range count, `complete`, source/consumer counts, and callback/stage event
ordering. Keep stub/image × c88=0/1 in the same build and run.

## Competing hypotheses and discriminating measurement

- H-TaskReporterUncalled: no `[audtask-join]` record is emitted for the target
  task interval.
- H-TaskReporterKeyMismatch: task records are emitted, but phase/event
  containment cannot associate them with the callback/stage candidate.
- H-TaskCompleteSemantics: the containing task record is associated and has
  ranges, but its `complete` field is only the PCM source+consumer predicate,
  so it remains zero without output publication.
- H-TaskReporterCaptureInvalid: oracle, route, phase, or candidate controls do
  not pass.

The discriminator is the single candidate-to-task interval table: zero
containing reporter rows selects H-TaskReporterUncalled; positive containing
rows with no candidate association selects H-TaskReporterKeyMismatch; a
positive association with `complete=0` and the reporter's documented
source/consumer predicate selects H-TaskCompleteSemantics; failed controls
select H-TaskReporterCaptureInvalid.

## Exact commands / controls

    rg -n -C 6 'audio_join_report_locked|audtask-join|complete =|g_audio_join_tasks' lib/N64ModernRuntime/librecomp/src/rsp.cpp
    rg -n -C 4 'audtask-image-complete-call|audtask-image-join|candidate-task-table' scratch/agent/run_s2345_m5_c88_downstream_ordinal_join.sh lib/N64ModernRuntime/librecomp/src/rsp.cpp
    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s2345_m5_c88_downstream_ordinal_join.sh s2386_m5_task_reporter_boundary

Expected controls are a successful build, title 1024, hangar 512, and all
four arms retained. A failed control selects H-TaskReporterCaptureInvalid;
do not change task data, audio, gate, fallback, dispatch, VI, or output
behavior.
