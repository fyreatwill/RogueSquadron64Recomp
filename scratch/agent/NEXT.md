# NEXT work unit — qualify port slot/status consumers in reachable hangar

HYPOTHESIS-ID: m5-step1-slot-status-consumer

Session 3329 established the correct route recipe: the image arm reaches
hangar VI-512/`0x006AB400` with autopilot presses at 60, 90, and 120 seconds
relative to title VI-1024. The prior 1,578 count was the cinematic dispatcher
pool, not the MusyX voice table. Do one like-for-like hangar qualification;
do not change behavior or add a mitigation.

## Competing hypotheses

- `H-PortMatchesRetail`: the port image arm now executes the same slot/status
  writer and consumer edges as retail in hangar; the remaining M5 gap is later
  output/contract behavior.
- `H-PortSlotStatusMissing`: the port reaches hangar but lacks the retail
  slot/status writes or consumer executions, so the image/PCM path still
  diverges before the downstream contract.
- `H-PortVoiceTableInactive`: the port's actual MusyX voice table remains
  inactive while retail's named consumers operate; this is the relevant audio
  divergence rather than cinematic-pool growth.

## Discriminator

One port run from `build/`, phase-gated to hangar VI-512, with the existing
task/PCM controls plus the slot/status consumers from Session 3327:

    ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
    ROGUESQ_SPIN_YIELD=1 ROGUESQ_STUB_MISSING_FUNCS=1
    ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_ROUTE_TRANSITION=1
    ROGUESQ_LOG_M5_VOICE_SLOTS=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1
    ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1
    ROGUESQ_LOG_M5_B40_ROUTE=1 ROGUESQ_LOG_M5_ROUTE_STATE=1
    ROGUESQ_AUTOPILOT='60:start,90:start,120:start'
    PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180
    PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1
    PROBE_KEYS='60:start 90:start 120:start'

Use `env ... zsh tools/probe.sh scratch/agent/s3330_m5_slot_status_qualification
240 1` and SIGKILL if the wrapper outlives its watchdog. Require positive
controls: VI-1024 and VI-512 phase rows, task dispatch, PCM source/consumer,
and the voice probe's initial arm row. Compare port rows against the retail
Session 3327 counts/PCs: slot range `0x141AD0:0x141AF0`, status range
`0x154620:0x1546A0`, and PCs `0x80094648`, `0x8009B600`, `0x8009B85C`,
`0x8009BDE8`.

Interpretation: matching hangar writer/consumer rows selects
`H-PortMatchesRetail`; absent port rows with valid phase/task/PCM controls
select `H-PortSlotStatusMissing`; an inactive voice mask alongside retail
consumer activity selects `H-PortVoiceTableInactive`. A crash before hangar
or missing phase/task controls is invalid and must not select a hypothesis.
