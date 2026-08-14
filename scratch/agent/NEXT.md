# NEXT work unit (s1062)

HYPOTHESIS-ID: retail-selector0-upstream-state

Perform one bounded static audit of the remaining producer boundary for the
case-0 argument byte at `0x80130B40`. Inspect the callers of the two
non-constant writers (`cinematicLoopBody` at `0x800A5E5C` and the
`menuOverlayInit` asset-table path at `0x800C5B8C`) only far enough to classify
their incoming values as controller input, timer/demo/attract state,
ordinary menu/ship/persistent state, or unresolved pointer/data state. Do not
build, run the game, or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-selector0-input`: an incoming value is directly derived from a controller edge or button mask.
* `H-selector0-demo`: an incoming value is directly derived from a timer, attract, or demo counter.
* `H-selector0-state`: both incoming values are menu, asset, save, ship, or cinematic state.
* `H-selector0-boundary`: an indirect/pointer-mediated producer remains unresolved.

Discriminating measurement: produce one source/caller table for the two
non-constant `0x80130B40` writers, including each incoming argument's
immediate reads and callers. A direct controller source selects input; a
timer/demo source selects demo; fully classified state-shaped inputs select
state; any unresolved pointer/data source keeps the boundary hypothesis open.
Do not infer from selector values or later dispatch.

Exact commands:

```sh
rg -n -B 18 -A 24 '0x800A5E5C|0x800C5B8C|cinematicLoopBody|menuOverlayInit' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -800
rg -n -B 18 -A 24 'jal.*0x800A5D80|0x800A5D80|jal.*0x800C58A0|0x800C58A0' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1000
rg -n -B 12 -A 22 'getController(New|Raw)|timer|demo|attract|loadCutscene|asset|save' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1000
```

Expected output is one complete producer/caller table for the two
non-constant `0x80130B40` writers, with a selected hypothesis or an explicitly
unresolved producer boundary. No build or runtime run is needed.
