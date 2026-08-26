# NEXT work unit (s2410) — resolve M5 identity-join defect

HYPOTHESIS-ID: m5-identity-join-defect

## Work unit

Add one batched identity-correlation table to the existing image-stage/PCM/
key-on diagnostics, rebuild once, and run the validated stub and image arms
one at a time. Correlate every target-phase image row with independent
key-on/transfer events by `(arm, VI origin, phase, ordinal/row, event
sequence)`, and report whether the join fails because of phase, ordinal/row,
or a missing producer-to-consumer sequence field. Do not change task data,
audio, gate, fallback, dispatch, VI, output behavior, or the nonzero
predicate.

## Competing hypotheses and discriminator

- H-PhaseKey: image and key-on records use different phase labels or VI-origin
  transitions, but match after phase/origin normalization.
- H-OrdinalRowKey: phase/origin match, but the producer uses a different
  ordinal/row convention; a shifted or transformed row joins the event.
- H-SequenceKey: neither phase nor row explains the mismatch; the missing
  key is a task/DMA/event sequence relationship.
- H-NoJoinAtCapture: independent key-on events still cannot be associated with
  any target image row after all three keys are tested.

The discriminator is one table containing all four candidate keys and counts
of rows joined by phase, ordinal/row, sequence, or not at all. A phase-only
join selects H-PhaseKey; an ordinal/row-only join selects H-OrdinalRowKey; a
sequence-only join selects H-SequenceKey; no join selects
H-NoJoinAtCapture. The image arm must still show stage rows and the stub arm
must still reach both route controls as positive controls.

## Exact commands

After the single rebuild, use the same phase-gated command as s2409, changing
only `ROGUESQ_AUDIO_UCODE=<0|1>` and the output directory:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=<0|1> ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1 ROGUESQ_LOG_INIT_VOICE_SAMPLE=1 ROGUESQ_LOG_M5_INIT_VOICE=1 ROGUESQ_LOG_M5_AUDIO_EVENT=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' ROGUESQ_DRAIN_INLOOP_TICK=1 zsh tools/probe.sh scratch/agent/s2409_downstream_range_identity/<arm> 75 1`

Run arm 0 then arm 1; preserve each `run.log`, and reduce the complete table
from both logs before interpreting any null.
