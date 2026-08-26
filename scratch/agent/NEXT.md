# NEXT work unit (s2480) — validate runtime SP completion consumption

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Run one qualified image-arm capture that verifies the runtime SP completion
message's complete lifecycle: event registration, `run_task` return,
`sp_complete` publication, and game-side queue consumption. Do not change
code, add a runtime API, add a NULL guard, or remap audio/output in this unit.

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
H-SPRegistrationGap. The positive control is the existing event-wiring
category itself: `[event-wiring] register` and `[event-wiring] complete kind=SP`
must both visibly fire, or the run is invalid.

## Exact command

Build is not needed. From the repo root, launch one qualified image-arm run
with a bounded watchdog and lifecycle logs, then inspect bounded rows:

```sh
mkdir -p scratch/agent/soak_results/s2480_runtime_sp_lifecycle
(cd build && env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 \
    ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_LOG_M5_TASK_CONTRACT=1 ROGUESQ_LOG_EVENT_WIRING=1 \
    ROGUESQ_LOG_AUDIO_RETURN=1 ./RogueSquadron64Recomp \
    > ../scratch/agent/soak_results/s2480_runtime_sp_lifecycle/run.log 2>&1) &
pid=$!; sleep 180; kill -KILL "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true
grep -n -E 'event-wiring.*(register|complete kind=SP)|audio-route.*(run-task-return|sp-complete)|audtask-abi' \
  scratch/agent/soak_results/s2480_runtime_sp_lifecycle/run.log | tail -120
```

The existing event-wiring positive control must pass in this same run. If the
queue lifecycle is complete, the next unit can audit the image downstream
consumer; if publication is not consumed, first locate the game queue consumer.
