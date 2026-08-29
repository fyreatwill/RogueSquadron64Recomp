# NEXT work unit — qualify the Step 6 drain-tick policy

HYPOTHESIS-ID: m5-audio-destub-step6-policy

## Single work unit

Build the centralized default-off drain-tick policy and the regeneration-safe
fixup together. Do not remove the status-03 wait hatch or alter a guest gate.

## Competing hypotheses

- `H-Step6-PolicyApplied`: an unset `ROGUESQ_DRAIN_INLOOP_TICK` reaches the
  generated drain loop as `0`, while explicit `=1` remains the control arm.
- `H-Step6-PolicyBypassed`: generated code still treats unset as enabled or
  the startup policy is not applied before the first drain call.
- `H-Step6-BuildRegression`: the policy source/fixup change does not compile
  or changes unrelated startup behavior.

## Discriminating measurement

One source/build check must show the helper call, the fixup's `=1` predicate,
and a successful target build. If a run is available, one same-build pair
must show `[drain-inloop-gate] en=0` with the default and `en=1` with the
explicit control. The result selects policy-applied, policy-bypassed, or
build-regression; no route-null is interpreted as audio evidence.

## Exact commands

```sh
rg -n 'rs64_m5_apply_drain_tick_policy|ROGUESQ_DRAIN_INLOOP_TICK|s1993_inloop_tick_en' src/main/main.cpp /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py
cmake --build build --config Debug --target RogueSquadron64Recomp
git diff --check
```
