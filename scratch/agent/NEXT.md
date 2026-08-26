# NEXT work unit (s2481) — validate target-route SP completion consumption

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Run one phase-valid qualified image-arm capture using the known eleven-Start
`tools/probe.sh` route. Verify the runtime SP completion message's complete
lifecycle: event registration, `run_task` return, `sp_complete` publication,
and game-side queue consumption. Do not change code, add a runtime API, add a
NULL guard, or remap audio/output in this unit.

## Competing hypotheses

- H-SPConsumed: the runtime publishes the registered SP message and the game
  consumes it after each image-arm task.
- H-SPPublishedUnconsumed: publication occurs, but the registered game queue
  does not consume it on this route.
- H-SPRegistrationGap: the SP event is missing or registered with the wrong
  queue/message before image tasks run.

## Discriminator

The same-run rows must show registration plus paired publication and consume
counts for the target image route. Registration + publication + consumption
selects H-SPConsumed; registration + publication with no consume selects
H-SPPublishedUnconsumed; absent/incorrect registration selects
H-SPRegistrationGap. The positive control is `[event-wiring] register` plus
`[event-wiring] complete kind=SP`, and the route control is a phase 512 row
with the hangar origin; both must fire in this run.

## Exact command

Build is not needed. From the repo root:

```sh
mkdir -p scratch/agent/soak_results/s2481_runtime_sp_lifecycle
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_EVENT_WIRING=1 \
  ROGUESQ_LOG_AUDIO_RETURN=1 PROBE_PHASE_WIDTH=512 \
  PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 \
  PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
  zsh tools/probe.sh scratch/agent/soak_results/s2481_runtime_sp_lifecycle 180 2
grep -n -E 'event-wiring.*(register|complete kind=SP)|audio-route.*(run-task-return|sp-complete)|audtask-abi' \
  scratch/agent/soak_results/s2481_runtime_sp_lifecycle/port.log | tail -120
```

If the route control fails again, do not interpret generic SP rows; classify
the capture as phase-invalid and diagnose the input/route gate next.
