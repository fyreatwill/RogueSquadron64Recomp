# NEXT work unit (s2756) — validate M5 AI status de-stub

HYPOTHESIS-ID: m5-ai-status-destub-validation

## Work unit

Validate `osAiGetStatus_recomp` on the qualified route with one phase-gated
run and both image and `ROGUESQ_AUDIO_UCODE=0` control arms in the same build.
Join AI status to buffered-byte state, task/SP completion, PCM joins, and route
phase. Evidence from this change is in
`scratch/agent/s2755_m5_ai_status/decision-table.txt`.

## Competing hypotheses and discriminator

- H1-live: status bit 0 tracks non-empty buffered audio and clears when empty.
- H2-unreachable: the qualified route never reaches the status query.
- H3-wrong-contract: the query is reached but disagrees with buffered state.

The discriminator is one phase-keyed row containing status, buffered bytes,
M_AUDTASK dispatch/exit, SP completion, PCM source/consumer, and route phase.
Both empty and non-empty buffer controls must be present in the same run.

## Exact commands

1. `env PROBE_PHASE_WIDTH=1 PROBE_KEYS_FROM_PHASE=1 ROGUESQ_LOG_ALL=1 zsh <qualified-driver>`
2. Run the same build with `ROGUESQ_AUDIO_UCODE=0`.
3. Save the bounded correlation under `scratch/agent/s2756_m5_ai_status/`.
