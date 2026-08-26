# NEXT work unit (s2383) — M5 task completion/output contract audit

HYPOTHESIS-ID: m5-task-output-gap

## Work unit

Audit the existing task-completion and PCM-publication joins behind the s2382
`H-TaskOutputGap` result. First enumerate the exact event fields and join
predicates used by the driver, then make one bounded instrumentation change
that reports every candidate task ordinal's completion bit, DMA range, PCM
source, PCM consumer, and render event in the same phase-keyed table. Keep
behavior unchanged and retain stub c0/c1 plus image c0/c1 arms in one build/run.

## Competing hypotheses and discriminating measurement

- H-CompletionEventMissing: the completion marker/event is absent or cannot
  join despite task-DMA/render rows; the missing event is upstream of output.
- H-CompletionBitFalse: completion rows exist and explicitly carry
  `complete=0` for candidate tasks; task execution reaches the boundary but
  does not publish completion.
- H-OutputConsumerMissing: completion is positive, but PCM source/consumer or
  render publication remains absent; the gap is downstream of completion.
- H-TaskOutputJoinInvalid: build, route, positive controls, or the complete
  candidate table fails, so no contract conclusion is valid.

The discriminator is one phase-keyed candidate row containing task ordinal,
dispatch/exit, completion bit, DMA start/length, source/consumer event, render
event, and route phase. A missing completion event selects
H-CompletionEventMissing; explicit completion rows with false bits select
H-CompletionBitFalse; positive completion with absent output selects
H-OutputConsumerMissing; failed controls or incomplete joins select
H-TaskOutputJoinInvalid.

## Exact commands / controls

Use the existing driver as the baseline and patch only its Python summary
table for the candidate-event census, after reading the event schemas:

    rg -n 'task_complete|pcm_source_joined|pcm_consumer_joined|render_rows|task_dma' scratch/agent/run_s2345_m5_c88_downstream_ordinal_join.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s2345_m5_c88_downstream_ordinal_join.sh

Expected controls are a successful build, first target 640, title 1024,
hangar 512, and all four arms retained. If any control or candidate field is
absent, classify H-TaskOutputJoinInvalid and do not change gate, fallback,
dispatch, VI, task, audio, guard, or mitigation behavior.
