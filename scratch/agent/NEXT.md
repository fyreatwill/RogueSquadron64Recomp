# NEXT work unit (s2384) — M5 completion-event producer audit

HYPOTHESIS-ID: m5-task-output-gap

## Work unit

Audit the completion-event producer/association exposed by the s2383
candidate census. Read the existing `rs64_audio_join_image_complete` call
sites and the task completion reporter, then add one bounded, behavior-neutral
counter/table that records every image-stage candidate and whether its
completion callback was invoked, including `(arm, phase, ordinal, row)`.
Retain the same four stub/image × c88 arms and use the existing route controls.

## Competing hypotheses and discriminating measurement

- H-CompletionProducerUncalled: candidate stage rows exist but no matching
  completion callback invocation occurs.
- H-CompletionJoinKeyMismatch: callbacks occur, but arm/phase/ordinal/row
  keys do not match the candidate rows.
- H-CompletionReporterSuppressed: matching callbacks occur but the reporter
  suppresses or fails to emit completion fields.
- H-CompletionAuditInvalid: controls or candidate census are incomplete.

The discriminator is one phase-keyed table joining every candidate stage row
to callback-invocation rows by the full key. Zero callback rows selects
H-CompletionProducerUncalled; callbacks with zero joins select
H-CompletionJoinKeyMismatch; positive joins with absent emitted completion
fields select H-CompletionReporterSuppressed; failed controls select
H-CompletionAuditInvalid.

## Exact commands / controls

    rg -n -C 5 'rs64_audio_join_image_complete|complete_event|audtask-image-stage-row' lib/N64ModernRuntime/librecomp/src/rsp.cpp scratch/agent/run_s2345_m5_c88_downstream_ordinal_join.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s2345_m5_c88_downstream_ordinal_join.sh s2384_m5_completion_producer_audit

Expected controls are a successful build, title 1024, hangar 512, and all
four arms retained. If any control fails, classify H-CompletionAuditInvalid
and do not change gate, fallback, dispatch, VI, task, audio, guard, or
mitigation behavior.
