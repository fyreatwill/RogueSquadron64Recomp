# NEXT work unit (s1057)

HYPOTHESIS-ID: retail-state-transition-input

Perform one bounded static audit of the producer feeding selector 0's case-0
frame result: enumerate the return-value branches in
`runHangarSelectionFrame`, especially the `0x00FFFFFE`/`0x00FFFFFF` sentinel
comparison consumed by `runHangarMenuFromOverlay`. Do not build, run the game,
or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-frame-ret-input`: a return branch or its immediate predicate is directly
  controlled by a controller edge or button-mask source.
* `H-frame-ret-demo`: a return branch or its immediate predicate is directly
  controlled by a timer, attract, or demo counter source.
* `H-frame-ret-state`: all return branches are controlled by menu state, asset,
  unlock, shutdown, or other persistent state without a local input/timer/demo
  source.

Discriminating measurement: produce one complete table of every return-value
write/branch in `runHangarSelectionFrame`, including the immediate predicate,
returned constant or register, and nearest producer. Any controller source
selects `H-frame-ret-input`; any timer/demo source selects `H-frame-ret-demo`;
if all rows are state/asset/unlock/shutdown sources, select
`H-frame-ret-state`. A missing sentinel return is a boundary result and must be
reported rather than inferred.

Exact commands:

```sh
rg -n -B 18 -A 24 'RECOMP_FUNC void runHangarSelectionFrame|0x00FFFFFE|0x00FFFFFF|jr.*ra|ctx->r2' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_28.c
rg -n -B 14 -A 18 'getControllerNewButtonsPressed|timer|demo|attract|unlock|runHangarSelectionFrame' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_28.c | head -1200
rg -n -B 12 -A 18 'runHangarSelectionFrame|0x00FFFFFE|0x00FFFFFF' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_35.c
```

Expected output is one complete frame-return branch table and a selected
hypothesis or an explicitly unresolved producer boundary. No build or runtime
run is needed.
