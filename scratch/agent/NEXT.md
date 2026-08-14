# NEXT work unit (s1061)

HYPOTHESIS-ID: retail-selector0-upstream-state

Perform one bounded static audit of the producer chain for the selector value
that reaches `menuOverlayInit` case 0 and calls `runHangarMenuFromOverlay`.
Start at the case-0 call site and trace the immediate `s3[0]`/selector source
and its writers only far enough to classify it as controller input,
timer/demo/attract state, ordinary menu/ship/persistent state, or an
unresolved boundary. Do not build, run the game, or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-selector0-input`: the value reaching case 0 is directly derived from a
  controller edge or button mask.
* `H-selector0-demo`: the value is directly derived from a timer, attract, or
  demo counter.
* `H-selector0-state`: the value is produced by menu, ship, asset, or
  persistent state with no direct input/demo source.
* `H-selector0-boundary`: an indirect/pointer-mediated producer remains
  unresolved.

Discriminating measurement: produce one source/caller table for the case-0
argument, listing every immediate writer and the reads on each chain. A direct
controller source selects input; a timer/demo source selects demo; fully
classified state-shaped writers select state; any unresolved writer keeps the
boundary hypothesis open. Do not infer from selector values or later dispatch.

Exact commands:

```sh
rg -n -B 24 -A 34 'runHangarMenuFromOverlay|menuOverlayInit|800CFF50|s3\[0\]' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -B 18 -A 26 'sw.*0x800CFF50|0x800C5A8C|0x800C5AF4|0x800C5B3C|selector' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -800
rg -n -B 12 -A 22 'getController(New|Raw)|timer|demo|attract|runHangarMenuFromOverlay' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -800
```

Expected output is one complete producer/caller table for the case-0
selector, with a selected hypothesis or an explicitly unresolved producer
boundary. No build or runtime run is needed.
