# NEXT work unit — obtain the VI-mode request state body

HYPOTHESIS-ID: vi640-maudtask-type2-writer

Session 3263 completed the local availability audit. The generated
`RecompiledFuncs/` tree is absent; `applyPendingViChanges` is available only
as symbol metadata and a probe-template call site. The next unit requires an
external generated body/provenance or an independent retail trace of its
state inputs.

## Competing hypotheses

- `H-RequestState`: an upstream state/branch prevents the target VI-mode
  request from being issued.
- `H-BoundaryConsumer`: a target request is issued but the VI consumer fails
  to commit it.
- `H-Phase4SteadyState`: width 640 is an intentional terminal route.
- `H-SourceUnavailable`: the generated body/state inputs are unavailable in
  this checkout, so the runtime hypotheses cannot yet be split.

## Discriminator

Obtain the generated body or an independent ground-truth trace of its state
inputs. A suppressed target request with a live state input selects
`H-RequestState`; a target request followed by no commit selects
`H-BoundaryConsumer`; an explicit terminal-route contract selects
`H-Phase4SteadyState`; continued source absence selects
`H-SourceUnavailable`.

## Exact commands

```sh
rg -n "vi_width|0066A500|update_screen|target|80019CD0|spTaskSchedulerThread|recv-scheduler-identity" src lib RecompiledFuncs patches tools
rg -n "phase=4|width=640|0066A500|VI-640" src docs tools scratch/agent/s3260_scheduler_identity.md
git diff -- src lib patches tools
```

Read only bounded windows around `applyPendingViChanges` and its state inputs
once the generated body is available. If it remains unavailable, obtain the
independent oracle trace instead; do not add another host-side field. No
scheduler/audio behavior change is authorized.
