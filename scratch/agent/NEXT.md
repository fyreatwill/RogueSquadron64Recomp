# NEXT work unit (s2408) — revalidate M5 two-arm route prerequisite

HYPOTHESIS-ID: m5-downstream-range-identity

## Work unit

Run the existing phase-gated Start-driver recipe one arm at a time from the
same built executable, with the complete downstream instrumentation enabled.
This is a prerequisite rerun after s2407's concurrent stub arm crashed before
the target phase. Do not change task data, audio, gate, fallback, dispatch,
VI, output behavior, or the nonzero predicate.

## Competing hypotheses and discriminator

- H-RouteDriverOnly: the s2407 stub miss was caused by concurrent-window/input
  focus interference; a sequential driver run reaches title and hangar.
- H-StubRouteCrash: the silent stub arm itself crashes before title even with
  valid phase-gated input.
- H-ImageRouteCrash: the image arm cannot reach both target phases under the
  same driver recipe.
- H-ControlsInvalid: either arm lacks a positive route control, so no
  downstream null may be interpreted.

The discriminator is one table per arm containing process result, first
`vi_width=1024 origin=0x790400`, first `vi_width=512 origin=0x6AB400`, and
counts of image-stage rows, image-DMA joins, PCM rows, and
`audtask-image-downstream` rows. Both arms reaching both target phases selects
H-RouteDriverOnly and authorizes repeating the downstream range comparison;
an arm-specific crash selects that route failure; missing controls selects
H-ControlsInvalid.

## Exact commands

Use the already-built image from s2407. For each arm, run:

`env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=<0|1> ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1 ROGUESQ_LOG_INIT_VOICE_SAMPLE=1 ROGUESQ_LOG_M5_INIT_VOICE=1 ROGUESQ_LOG_M5_AUDIO_EVENT=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 PROBE_KEYS='3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start' ROGUESQ_DRAIN_INLOOP_TICK=1 zsh tools/probe.sh scratch/agent/s2408_downstream_range_identity/<arm> 75 1`

Run arm 0 then arm 1; preserve each `run.log`. Kill survivors with SIGKILL
through `tools/probe.sh`. Do not build unless the executable is stale.
