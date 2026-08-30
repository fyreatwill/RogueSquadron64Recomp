# NEXT work unit — obtain the VI-mode request state body

HYPOTHESIS-ID: vi640-maudtask-type2-writer

Session 3262 found that the local checkout cannot perform the requested state
audit: the generated `RecompiledFuncs/` tree is absent. The only local
reference is the probe template's expected caller at `0x80019914`; host VI
wrappers observe requests but do not choose them.

## Competing hypotheses

- `H-RequestState`: an upstream state/branch prevents the target VI-mode
  request from being issued.
- `H-BoundaryConsumer`: a target request is issued but the VI consumer fails
  to commit it.
- `H-Phase4SteadyState`: width 640 is an intentional terminal route.
- `H-SourceUnavailable`: the generated body/state inputs are unavailable in
  this checkout, so the three runtime hypotheses cannot yet be split.

## Discriminator

Obtain the generated body or an independent ground-truth trace of its state
inputs. A suppressed target request with a live state input selects
`H-RequestState`; a target request followed by no commit selects
`H-BoundaryConsumer`; an explicit terminal-route contract selects
`H-Phase4SteadyState`. If the body cannot be supplied, record the external
dependency rather than adding another host-side field.

## Exact commands

```sh
rg -n "vi_width|0066A500|update_screen|target|80019CD0|spTaskSchedulerThread|recv-scheduler-identity" src lib RecompiledFuncs patches tools
rg -n "phase=4|width=640|0066A500|VI-640" src docs tools scratch/agent/s3260_scheduler_identity.md
git diff -- src lib patches tools
```

Read only bounded windows around `applyPendingViChanges` and its state inputs
once the generated body is available. No scheduler/audio behavior change is
authorized. Build/run only if the body identifies a complete existing positive
control and a discriminating capture.

Do not repeat the completed boundary capture or add another source field.
