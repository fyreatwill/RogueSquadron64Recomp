# Next work unit: qualify the port target phase before route parity

HYPOTHESIS-ID: m5-port-target-phase-qualification

The s3821 retail/port pair was coverage-invalid: retail reached the qualified
hangar snapshot, while the corrected port arm was stable but remained at VI
640. Do one single-port image-arm qualification using the exact validated
autopilot route and the existing phase/task/source controls. Do not run the
retail oracle in this unit.

Competing hypotheses and discriminator:

- H1: the port image route reaches title 1024 and hangar 512 when run alone;
  the paired failure was launch interaction or timing.
- H2: the port route itself stalls at 640 under the current build/config;
  target-phase parity cannot yet be measured.
- H3: the run is coverage-invalid because a phase/task/source positive control
  is absent even if a target-width line appears.

The discriminator is one 90-second single-port run. H1 requires phase 1024 and
512, task/route/source controls, and no crash/abort. H2 is stable 640-only
execution with controls but no target phase. H3 is any missing positive control
or contradictory phase evidence.

Command:

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 \
      ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
      ROGUESQ_DRAIN_INLOOP_TICK=1 ROGUESQ_LOG_PHASE=1 \
      ROGUESQ_LOG_M5_FREQUENCY_CALLERS=1 ROGUESQ_LOG_M5_ROUTE_ORDER=1 \
      ROGUESQ_LOG_M5_RSP_SOURCE=1 ROGUESQ_LOG_M5_SOURCE_WRITER=1 \
      ROGUESQ_LOG_M5_SOURCE_PRODUCER=1 ROGUESQ_LOG_M5_SOURCE_TRANSITION=1 \
      ROGUESQ_LOG_M5_TASK_CONTRACT=1 \
      ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
      ROGUESQ_AUTOPILOT_STOP_WIDTH=512 ROGUESQ_AUDIO_UCODE=1 \
      ./build/RogueSquadron64Recomp > scratch/agent/s3822_port_target.log 2>&1

Inspect bounded `[phase]`, route, RSP-source, source-producer, task-contract,
`[CRASH]`, and `[ABORT]` lines only. Kill with SIGKILL after 90 seconds if the
process remains alive.
