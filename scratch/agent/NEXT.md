# NEXT work unit (s1054)

HYPOTHESIS-ID: retail-state-transition-input

Perform one bounded static audit of the `menuOverlayInit` selector-9 path
entered by the width-320 caller. Trace the case-9 handler and its immediate
state updates until the next read/write of `0x800CFF50` (the selector
halfword). Do not build, run the game, or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-selector-input`: case 9 reaches index 0 through a controller edge or
  button-mask source.
* `H-selector-demo`: case 9 reaches index 0 through a timer, attract, or demo
  counter source.
* `H-selector-state`: case 9 reaches index 0 through persistent, asset,
  unlock, or return-value state with no local input/timer source.

Discriminating measurement: produce one bounded case-9 dataflow table showing
the handler entry, every branch feeding the write/read of selector halfword
`0x800CFF50`, and each source's nearest producer. A controller source selects
`H-selector-input`; timer/demo data selects `H-selector-demo`; persistent,
asset, unlock, or return-value data selects `H-selector-state`. If the case-9
handler target is unresolved, report that exact unresolved edge instead of
widening the sweep.

Exact commands:

```sh
rg -n -B 25 -A 45 'addiu.*0x9|0x8003E084|0x800C58A0' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_8.c | head -1000
rg -n -B 18 -A 24 '0x800CFF50|0x800D.*0xB0|0x800A75C0|runHangarMenuFromOverlay|getControllerNewButtonsPressed|timer|demo|attract' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1800
```

Expected output is one case-9 selector dataflow table and a selected
hypothesis or an explicitly unresolved handler edge. No build or runtime run
is needed.
