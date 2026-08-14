# NEXT work unit (s1058)

HYPOTHESIS-ID: retail-state-transition-input

Perform one bounded static audit of `accumulateShipThrottleCharge`, the
ordinary return producer left open by s1057. Do not build, run the game, or
arm a freelist watch.

Competing hypotheses and discriminator:

* `H-throttle-ret-input`: a return branch or its immediate predicate reads a
  controller edge or button mask.
* `H-throttle-ret-demo`: a return branch or its immediate predicate reads a
  timer, attract, or demo counter.
* `H-throttle-ret-state`: all return branches are driven by throttle/ship/menu
  state, asset, or persistent values, with no local input/timer/demo source.

Discriminating measurement: produce one complete table of every return-value
write/branch in `accumulateShipThrottleCharge`, including the branch address,
predicate, returned constant/register, and nearest producer for the two global
values consumed by `runHangarSelectionFrame` (`0x800D:0xFFFFD6D4` and
`0x800D:0xFFFFD6D0`). Any direct controller source selects input; any direct
timer/demo source selects demo; otherwise select state. A missing writer or
unresolved helper is a boundary result and must be reported, not inferred.

Exact commands:

```sh
rg -n '^RECOMP_FUNC .*accumulateShipThrottleCharge|0x800B4168' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_28.c
rg -n -B 16 -A 24 'accumulateShipThrottleCharge|FFFFD6D4|FFFFD6D0|0x800AB188|jr.*ra' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_28.c
rg -n -B 12 -A 18 'getControllerNewButtonsPressed|timer|demo|attract|accumulateShipThrottleCharge' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_28.c | head -600
```

Expected output is one complete ordinary-return branch table and a selected
hypothesis or an explicitly unresolved producer boundary. No build or runtime
run is needed.
