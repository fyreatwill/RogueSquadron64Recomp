# NEXT work unit (s1060)

HYPOTHESIS-ID: retail-state-transition-input

Perform one bounded static audit of the immediate callers and data producers
behind the two state/table-derived stores of `0x800CD6D4` at `0x800AC914` and
`0x800AD0DC`. Trace the indexed source `D_800D291C + (0x800D-0x3C08)` and
the helper `updateTextOverlayLookupEntry` only far enough to classify whether
the selected byte is supplied by controller input, timer/demo/attract state,
ordinary menu/ship state, or an unresolved boundary. Do not build, run the
game, or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-exit-word-input`: either store's source chain reads a controller edge or
  button mask.
* `H-exit-word-demo`: either source chain reads a timer, attract, or demo
  counter.
* `H-exit-word-state`: both source chains are menu/ship/asset/persistent state.
* `H-exit-word-boundary`: an indexed table producer or helper remains
  unresolved, so classification must stay open.

Discriminating measurement: produce one table for both store sites listing the
indexed-address calculation, source-byte writer(s), helper/caller chain, and
any controller/timer/demo reads. A direct input source selects input; a direct
timer/demo source selects demo; fully classified state-shaped chains select
state; any unresolved producer selects boundary. Do not infer from the byte's
value or from the destination's later use.

Exact commands:

```sh
rg -n -B 18 -A 26 '0x800AC914|0x800AD0DC|updateTextOverlayLookupEntry|D_800D291C|-0x3C08' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -B 10 -A 18 'MEM_[WBH].*0X291C|MEM_[WBH].*0X3C08|0x800D291C|0x800D3C08' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -B 12 -A 18 'getController(New|Raw)|timer|demo|attract|updateTextOverlayLookupEntry' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -800
```

Expected output is one complete source/caller table for both ordinary stores,
with a selected hypothesis or an explicitly unresolved producer boundary. No
build or runtime run is needed.
