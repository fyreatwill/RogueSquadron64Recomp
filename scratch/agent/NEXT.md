# NEXT work unit (s2409) — repeat M5 downstream-range comparison

HYPOTHESIS-ID: m5-downstream-range-identity

## Work unit

Run the existing phase-gated Start-driver recipe one arm at a time from the
same built executable, with the complete downstream instrumentation enabled.
The route prerequisite is now valid; compare the exact image-DMA range with
same-identity PCM, slot-sb, and keyon-w40 observations. Do not change task
data, audio, gate, fallback, dispatch, VI, output behavior, or the nonzero
predicate.

## Competing hypotheses and discriminator

- H-ConsumerAtImageRange: same-identity post-DMA slot/keyon events occur at the
  exact image DMA destination, so the zero image rows are a legitimate
  consumer boundary.
- H-ConsumerAtPCMRange: the slot/keyon consumer follows the PCM range rather
  than the image DMA destination; image-range stage-only rows are expected.
- H-NoPostDMAConsumer: neither range has a matching post-DMA slot/keyon event
  in the target phase, so the current capture edge is incomplete.
- H-IdentityJoinDefect: the route is valid but ordinal/row identity fails to
  join the real consumer; matching events appear only under a distinct key.

The discriminator is one target-phase table per image arm containing each
same-identity image-DMA range, PCM range, first post-DMA `slot-sb` range, and
first `keyon-w40` range, plus counts of exact-range, PCM-range, no-consumer,
and unmatched-identity rows. A consumer at the image range selects
H-ConsumerAtImageRange; a consumer only at the PCM range selects
H-ConsumerAtPCMRange; no events selects H-NoPostDMAConsumer; events under a
different key select H-IdentityJoinDefect. The stub arm remains the positive
silent-control baseline and must still reach both route phases.

## Exact commands

Use the already-built image from s2408. For each arm, run the same command as
s2408, changing only `ROGUESQ_AUDIO_UCODE=<0|1>` and the output directory:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=<0|1> ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1 ROGUESQ_LOG_INIT_VOICE_SAMPLE=1 ROGUESQ_LOG_M5_INIT_VOICE=1 ROGUESQ_LOG_M5_AUDIO_EVENT=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' ROGUESQ_DRAIN_INLOOP_TICK=1 zsh tools/probe.sh scratch/agent/s2409_downstream_range_identity/<arm> 75 1`

Run arm 0 then arm 1; preserve each `run.log`. Kill survivors with SIGKILL
through `tools/probe.sh`.
