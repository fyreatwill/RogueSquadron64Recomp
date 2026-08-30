# NEXT work unit — identify the VI-mode request state

HYPOTHESIS-ID: vi640-maudtask-type2-writer

Session 3261 selected the VI-mode publication edge: after phase 4 began at
width 640/origin `0x0066A500`, `applyPendingViChanges` made one same-width
request, while receive and route-preparation activity continued. No 1024
request or target origin appeared.

## Competing hypotheses

- `H-RequestState`: an upstream state/branch prevents the target VI-mode
  request from being issued.
- `H-BoundaryConsumer`: a target request is issued but the VI consumer fails
  to commit it.
- `H-Phase4SteadyState`: width 640 is an intentional terminal route.

## Discriminator

Enumerate the state inputs and branches feeding `applyPendingViChanges` and
map them to existing mode/phase rows. A suppressed target request with a live
state input selects `H-RequestState`; a target request followed by no commit
selects `H-BoundaryConsumer`; an explicit terminal-route contract selects
`H-Phase4SteadyState`. Do not add a runtime field until the source audit names
the state edge and an existing positive control.

## Exact commands

```sh
rg -n "vi_width|0066A500|update_screen|target|80019CD0|spTaskSchedulerThread|recv-scheduler-identity" src lib RecompiledFuncs patches tools
rg -n "phase=4|width=640|0066A500|VI-640" src docs tools scratch/agent/s3260_scheduler_identity.md
git diff -- src lib patches tools
```

Read only bounded windows around `applyPendingViChanges` and its state inputs.
No scheduler/audio behavior change is authorized. Build/run only if the audit
identifies a complete existing positive control and a discriminating capture.

Do not repeat the completed boundary capture or add another source field.
