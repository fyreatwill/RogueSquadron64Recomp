# NEXT work unit — audit the missing target-phase boundary

HYPOTHESIS-ID: vi640-maudtask-type2-writer

Session 3260 established that the repaired identity probe is live: phase-2
accepted rows carried valid message pointers and types `0x02/0x01/0x81`, with
`89F/28D44`; positive controls fired. The run stayed at phase 4 width 640,
origin `0x0066A500`, and never reached the target VI-640 wall.

## Competing hypotheses

- `H-BoundaryProducer`: a pre-target producer/state transition fails to publish
  the message or VI/output state needed to leave width 640.
- `H-BoundaryConsumer`: the message stream is present, but a scheduler/VI
  consumer or gate does not accept the transition.
- `H-Phase4SteadyState`: width 640 is an intentional steady state in this
  route, so the missing target row is not a scheduler message defect.

## Discriminator

Enumerate the phase-4 width-640 producer/consumer/state edges in the checked-in
port and map each to the existing phase logger. The discriminator is one
named edge with an observable state change: a missing producer publication
selects `H-BoundaryProducer`; a present publication with no consumer advance
selects `H-BoundaryConsumer`; an explicit route contract proving width 640 is
terminal selects `H-Phase4SteadyState`. Do not add a new runtime field until
the source audit identifies the edge and its existing positive control.

## Exact commands

```sh
rg -n "vi_width|0066A500|update_screen|target|80019CD0|spTaskSchedulerThread|recv-scheduler-identity" src lib RecompiledFuncs patches tools
rg -n "phase=4|width=640|0066A500|VI-640" src docs tools scratch/agent/s3260_scheduler_identity.md
git diff -- src lib patches tools
```

Read only bounded windows around the scheduler/VI/output matches. This is a
static boundary audit; no build or game run is authorized unless it identifies
a complete existing A/B arm and a discriminating measurement.

## Exact start

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
sh -c 'env ROGUESQ_RECV_TRACE=1 ROGUESQ_LOG_ALL=1 ./RogueSquadron64Recomp > ../scratch/agent/s3260_scheduler_identity.log 2>&1 & p=$!; sleep 60; kill -9 "$p" 2>/dev/null || true; wait "$p" 2>/dev/null || true'
```

Do not add another source field or repeat the old unguarded probe. If the
repaired run does not reach VI 640, classify it as unevaluable and audit only
the new fault site.
