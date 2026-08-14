# NEXT work unit (s1055)

HYPOTHESIS-ID: retail-state-transition-input

Perform one bounded static audit of the selector-0/index-0 path in
`menuOverlayInit`. Trace the `runHangarMenuFromOverlay` call at
`0x800C5A8C` and its immediate return/state updates until the next read or
write of `0x800CFF50`. Do not build, run the game, or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-index0-input`: the case-0 handler reaches or leaves index 0 through a
  controller edge or button-mask source.
* `H-index0-demo`: the case-0 handler reaches or leaves index 0 through a
  timer, attract, or demo counter source.
* `H-index0-state`: the case-0 handler reaches or leaves index 0 through
  persistent, asset, unlock, or return-value state with no local input/timer
  source.

Discriminating measurement: produce one bounded case-0 dataflow table listing
the handler entry, every branch and return value that feeds selector state,
and each source's nearest producer. A controller source selects
`H-index0-input`; timer/demo data selects `H-index0-demo`; persistent,
asset, unlock, or return-value data selects `H-index0-state`. If the handler
does not touch selector state, record that exact boundary and classify only the
sources actually observed.

Exact commands:

```sh
rg -n -B 12 -A 70 'L_800C5A84|runHangarMenuFromOverlay|0x800C5A8C|0x800C5AA8|0x800C5AAC|0x800C5C3C' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_34.c
rg -n -B 18 -A 24 '0x800CFF50|0x800D.*0xB0|runHangarMenuFromOverlay|getControllerNewButtonsPressed|timer|demo|attract|isUnlockBitSet' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1800
```

Expected output is one case-0 selector dataflow table and a selected
hypothesis or an explicitly unresolved handler boundary. No build or runtime
run is needed.
