# NEXT work unit (s2413) — corroborate M5 sequence-key identity

HYPOTHESIS-ID: m5-identity-join-defect

## Work unit

Run one fresh image-arm capture with the rebuilt retained-stage table. The
valid s2412 image run selected `H-SequenceKey` (1,161 phase-only, 10
phase-plus-sequence, 2 all-key rows), but the silent-stub control again died
before title and is not comparable. Do not rerun the invalid stub arm. Require
title and hangar phase controls plus the key-on positive control before
reducing the table. Do not change task data, audio, gate, fallback, dispatch,
VI, output behavior, or the nonzero predicate.

## Competing hypotheses and discriminator

- H-PhaseKey: image and key-on records use different phase labels or VI-origin
  transitions, but match after phase/origin normalization.
- H-OrdinalRowKey: phase/origin match, but the producer uses a different
  ordinal/row convention; a shifted or transformed row joins the event.
- H-SequenceKey: neither phase nor row explains the mismatch; the missing key
  is a task/DMA/event sequence relationship.
- H-NoJoinAtCapture: independent key-on events still cannot be associated with
  any target image row after all three keys are tested.

The discriminator remains one table containing all four candidate keys and
counts of rows joined by phase/origin, ordinal/row, bounded sequence, or not
at all. The sequence candidate is the first key-on event after the image-stage
event and within 64 join events, regardless of route labels. Reproduction of
the class-5/class-7 population selects `H-SequenceKey`; a phase-only table
reopens `H-IdentityJoinDefect`; no stage rows or no key-on positive control is
route-invalid. Rows are capped at 512 per target phase and key-on history at
4096 per target phase.

## Exact commands

No rebuild is needed unless the current binary is absent. Use the rebuilt
retained-table binary and this phase-gated image command, changing only the
output directory:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1 ROGUESQ_LOG_INIT_VOICE_SAMPLE=1 ROGUESQ_LOG_M5_INIT_VOICE=1 ROGUESQ_LOG_M5_AUDIO_EVENT=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' ROGUESQ_DRAIN_INLOOP_TICK=1 zsh tools/probe.sh scratch/agent/s2413_identity_join/image 75 1`

Preserve `run.log` and reduce the complete table before interpreting any
null.
