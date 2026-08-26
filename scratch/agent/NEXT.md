# NEXT work unit (s2385) — M5 task completion reporter/association audit

HYPOTHESIS-ID: m5-task-output-gap

## Work unit

Audit the task completion reporter/association after s2384 showed that the
image completion callback is invoked and its completion event is attached to
stage candidates. Read the existing task reporter and its call sites, then add
one bounded, behavior-neutral table that joins each target completion callback
to task records by `(arm, phase, ordinal, row)` and records whether the task
completion bit/count is emitted. Retain the same four stub/image × c88 arms
and existing route controls.

## Competing hypotheses and discriminating measurement

- H-TaskReporterUncalled: completion callbacks occur but no task reporter
  invocation is associated with the target key.
- H-TaskCompletionBitSuppressed: task reporter invocation occurs but emits no
  completion bit/count on the containing task.
- H-TaskCompletionJoinKeyMismatch: task records exist but their association
  key differs from the callback's arm/phase/ordinal/row.
- H-CompletionAuditInvalid: controls or candidate census are incomplete.

The discriminator is one phase-keyed table joining every callback row to task
reporter rows and containing-task completion fields by the full key. Zero
reporter rows selects H-TaskReporterUncalled; positive reporter joins with
absent task completion fields selects H-TaskCompletionBitSuppressed; task rows
with no full-key joins selects H-TaskCompletionJoinKeyMismatch; failed
controls select H-CompletionAuditInvalid.

## Exact commands / controls

    rg -n -C 5 'complete_event|task.*complete|complete.*task|audtask-image-complete-call' lib/N64ModernRuntime/librecomp/src/rsp.cpp src/main/main.cpp scratch/agent/run_s2345_m5_c88_downstream_ordinal_join.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s2345_m5_c88_downstream_ordinal_join.sh s2384_m5_completion_producer_audit

Expected controls are a successful build, title 1024, hangar 512, and all
four arms retained. If any control fails, classify H-CompletionAuditInvalid
and do not change gate, fallback, dispatch, VI, task, audio, guard, or
mitigation behavior.
