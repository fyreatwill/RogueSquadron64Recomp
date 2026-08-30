# NEXT work unit — capture retail VI request-state inputs

HYPOTHESIS-ID: vi640-maudtask-type2-writer

The local source-availability arm is closed as `H-SourceUnavailable`:
`RecompiledFuncs/` is absent, and `applyPendingViChanges` is available only as
symbol metadata plus the probe-template caller. The next unit must use the
independent retail oracle or supplied regeneration artifact; do not repeat the
local inventory or add a port-side field.

## Competing hypotheses

- `H-RequestState`: an upstream state/branch prevents the target VI-mode
  request from being issued.
- `H-BoundaryConsumer`: a target request is issued but the VI consumer fails
  to commit it.
- `H-Phase4SteadyState`: width 640 is an intentional terminal route.
- `H-SourceUnavailable`: the generated body/state inputs are unavailable in
  this checkout. Selected for the local arm only.

## Discriminator

Obtain the generated body or an independent ground-truth trace of the state
inputs. A live state input with no target request selects `H-RequestState`; a
target request followed by no commit selects `H-BoundaryConsumer`; an explicit
terminal-route contract selects `H-Phase4SteadyState`. Continued absence is an
external dependency, not a runtime conclusion.

## Exact commands

```sh
test -x tools/oracle/build/rs64_oracle
tools/oracle/build/rs64_oracle --core "$ORACLE_CORE" --rom "$RETAIL_ROM" \
  --secs 180 --watch-write 0x0:0x800000 \
  --watch-pc 0x8001B7F0 --pc-phase-log-width 640 \
  --vi-trace --hit-cap 64
```

The run is valid only if the whole-RDRAM watch fires and the VI trace reaches
the target boundary. Add a focused watch for the state addresses once the
generated body or its provenance identifies them. A live state input with no
target request selects `H-RequestState`; a target request with no commit
selects `H-BoundaryConsumer`; an explicit terminal contract selects
`H-Phase4SteadyState`. If either oracle dependency is absent, record that
setup fact and do not claim a runtime hypothesis. No scheduler/audio behavior
change is authorized.
