# NEXT work unit (s2412) — obtain valid M5 image-arm identity capture

HYPOTHESIS-ID: m5-identity-join-defect

## Work unit

Rerun the already-built image arm with the bounded identity table, using the
known-good phase-gated driver and a fresh output directory. The s2411 image
attempt died pre-title at guest PC `0x8000B650`, while the same-binary stub
control reached title and hangar and fired `keyon-w40`; therefore no identity
hypothesis was selected. If the image arm reaches both target phases, run the
stub control once with the same binary and reduce the complete table. Do not
change task data, audio, gate, fallback, dispatch, VI, output behavior, or the
nonzero predicate.

## Competing hypotheses and discriminator

- H-PhaseKey: image and key-on records use different phase labels or VI-origin
  transitions, but match after phase/origin normalization.
- H-OrdinalRowKey: phase/origin match, but the producer uses a different
  ordinal/row convention; a shifted or transformed row joins the event.
- H-SequenceKey: neither phase nor row explains the mismatch; the missing key
  is a task/DMA/event sequence relationship.
- H-NoJoinAtCapture: independent key-on events still cannot be associated with
  any target image row after all three keys are tested.

The discriminator is one table containing all four candidate keys and counts
of rows joined by phase/origin, ordinal/row, bounded sequence, or not at all.
The sequence candidate is the first key-on event after the image-stage event
and within 64 join events, regardless of route labels. A phase-only join,
ordinal/row-only join, sequence-only join, or no join selects the corresponding
hypothesis. The image arm must show stage rows and reach both route controls;
otherwise the result is route-invalid. The stub arm must reach both controls
and fire the key-on positive control. Rows are capped at 512 per target phase
and key-on history at 4096 per target phase.

## Exact commands

No rebuild is needed unless the current binary is absent. Use the same
phase-gated command as s2409, first with `ROGUESQ_AUDIO_UCODE=1` and then with
`=0`, changing only the output directory:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=<0|1> ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1 ROGUESQ_LOG_INIT_VOICE_SAMPLE=1 ROGUESQ_LOG_M5_INIT_VOICE=1 ROGUESQ_LOG_M5_AUDIO_EVENT=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' ROGUESQ_DRAIN_INLOOP_TICK=1 zsh tools/probe.sh scratch/agent/s2412_identity_join/<arm> 75 1`

Run the image arm first; preserve each `run.log`, and reduce the complete
table from both logs before interpreting any null.
