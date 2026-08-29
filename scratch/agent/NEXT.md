# NEXT work unit — obtain a target-phase route change for M5

HYPOTHESIS-ID: m5-target-phase-route-boundary

## Single work unit

M5 is blocked at VI 640 in the Session 3192 same-build image-versus-silent
pair. The next unit requires a human-selected route change, or an equivalent
retail-grounded boundary, that makes the image arm reach title or hangar.
Do not repeat the same pair before that change.

Competing hypotheses and the discriminating measurement:

- `H-RouteOnly`: the VI-640 stop is route-specific and a selected route change
  reaches the target phase.
- `H-AudioPath`: the image/silent arm difference changes target-phase reachability
  only after a valid audio task/service boundary is selected.
- `H-Blocked`: no authorized route change is available; the target-phase nulls
  remain unevaluable.

The discriminator is the first phase-gated same-build pair after the route
change: title/hangar VI transition, image-arm DMEM/DMA/SP/service joins, and
silent-arm no-write control. The result must distinguish target-phase audio
execution from another pre-title route stop.

Exact commands after the human selects the route/configuration:

```sh
zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh s3214_m5_route_requal
```

Until that human input exists, do not build or launch a substitute route. The
current iteration is blocked pending that input.

Expected outcome: target phase reached with the required positive controls,
or the route remains pre-title and M5 stays blocked. If blocked, ask the human
to select the route/configuration before any build or run.
