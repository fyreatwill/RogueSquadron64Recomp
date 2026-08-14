# NEXT work unit (s1053)

HYPOTHESIS-ID: retail-state-transition-input

Perform one bounded static audit of the state producer that makes
`mainGameLoop` enter the width-320 `menuOverlayInit` call path. Trace the
construction of `s4`/`s5` and the value read at `s4+0x20` immediately before
the `0x8003E07C` gate. Do not build, run the game, or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-state-input`: the upstream byte is copied or set from controller edge or
  button-mask data.
* `H-state-demo`: the upstream byte is driven by timer/demo/attract state.
* `H-state-persistent`: the upstream byte comes from persistent/settings,
  overlay state, or a return value without a local input/timer source.

Discriminating measurement: produce one bounded writer/producer table for the
exact value consumed as `MEM_BU(ctx->r20, 0x20)` at `0x8003E07C`, including the
base pointer's construction, every direct store/copy into that byte or its
source field, and the guarding branch. A controller source selects
`H-state-input`; timer/demo-only data selects `H-state-demo`; persistent,
overlay, or return-value data with no input/timer source selects
`H-state-persistent`. If the base pointer cannot be resolved from generated
code, report that exact unresolved edge rather than widening the sweep.

Exact commands:

```sh
rg -n -B 20 -A 20 '0x8003E07C|MEM_BU\(ctx->r20, 0X20\)|ctx->r20 =|s4' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_8.c | head -1200
rg -n -B 12 -A 12 '0x80130B60|0x80130B40|0x20\)|getController|buttons|demo|timer|attract' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1600
```

Expected output is one producer/base-pointer table and a selected hypothesis
or an explicitly unresolved source. No build or runtime run is needed.
