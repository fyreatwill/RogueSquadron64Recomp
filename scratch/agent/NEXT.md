# NEXT work unit — obtain a new retail-grounded M5 boundary

HYPOTHESIS-ID: m5-retail-boundary-new-angle

## Single work unit

Choose one unenumerated retail instruction at the pre-title VI handoff using
static call/data-flow evidence, arm it with the whole-RDRAM positive control,
and run one phase-gated oracle capture through title and hangar. Do not add a
port instrument or change audio behavior until the oracle names a live writer
or consumer edge.

## Competing hypotheses

- H-RetailBoundaryFound: the new candidate executes in title or hangar and
  identifies the missing 640-to-1024 publication edge.
- H-RetailBoundaryAbsent: the candidate is live only in the 640 control or
  never executes, so it is not the target handoff.
- H-SourceInsufficient: the available static sources cannot justify a new
  candidate; no instrument should be built.

## Discriminating measurement

The same oracle run must show the whole-RDRAM control, title `1024`, hangar
`512`, and candidate-PC hits phase-keyed by VI origin. Target-phase candidate
hits select H-RetailBoundaryFound; control-only or zero hits select
H-RetailBoundaryAbsent; no defensible candidate selects H-SourceInsufficient.

## Exact command

```sh
rg -n 'pending|descriptor|osViSetMode|__osViSwapContext|VI_ORIGIN_REG' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 \
  syms docs --glob '!PORTING-STATE.md'
```

Before any build, record the candidate table and positive-control watch in
this file. If no candidate is defensible, perform no instrument build and
return to the parked external boundary with a falsifiable source request.
