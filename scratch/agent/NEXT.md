# NEXT work unit (s1063)

HYPOTHESIS-ID: retail-selector0-state-field-writers

Perform one bounded static audit of the global state byte read as `0x80130B54`
by the menu asset path at `0x800C5B8C`. Enumerate generated stores to that
byte, including stores expressed as a base `0x80130B40` plus offset `0x14` or
as equivalent register-derived addresses. Do not build, run the game, or arm
a freelist watch.

Competing hypotheses and discriminator:

* `H-field-input`: a writer directly derives the byte from a controller edge
  or button mask.
* `H-field-demo`: a writer directly derives it from a timer, attract, or demo
  counter.
* `H-field-state`: every generated writer is reset, menu, asset, save, ship,
  or cinematic state shaped.
* `H-field-boundary`: a writer remains unresolved because it is pointer-
  mediated, non-generated, or outside the searched address forms.

Discriminating measurement: produce one complete writer table for
`0x80130B54`, recording each store PC, address construction, value source,
and immediate callers/guards. A direct controller source selects input; a
timer/demo source selects demo; fully classified state-shaped writers select
state; any unresolved writer keeps the boundary hypothesis open.

Exact commands:

```sh
rg -n -B 16 -A 20 '0x80130B40|0X80130B40|0xB40|0XB40|0x14|0X14' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1600
rg -n -B 16 -A 20 'MEM_[BHW]\([^)]*0x14|MEM_[BHW]\([^)]*0X14|MEM_[BHW]\([^)]*0xB40|MEM_[BHW]\([^)]*0XB40' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1600
rg -n -B 12 -A 18 'getController(New|Raw)|timer|demo|attract|menu|asset|save|ship|cutscene' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1200
```

Expected output is one complete generated-tree writer/caller table for
`0x80130B54`, with a selected hypothesis or an explicitly unresolved writer
boundary. No build or runtime run is needed.
