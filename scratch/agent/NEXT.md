# NEXT work unit (s1064)

HYPOTHESIS-ID: retail-selector-upstream-state

Perform one bounded static audit of the fixed table byte selected by
`0x80130B54` in `menuOverlayInit`: enumerate generated writers to
`0x800D-0x2BFC + index`, and classify whether the table is immutable in the
generated tree or has state/input/demo-shaped updates. Do not build, run the
game, or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-table-immutable`: the generated tree has no writer to the table.
* `H-table-input`: a generated writer derives a table byte from controller
  state.
* `H-table-demo`: a generated writer derives a table byte from timer, attract,
  or demo state.
* `H-table-state`: generated writers are setup/menu/asset/save/ship/cinematic
  state shaped.
* `H-table-boundary`: a writer remains unresolved because it is pointer-
  mediated, non-generated, or outside the searched address forms.

Discriminating measurement: produce one complete writer table for the table
range, recording each store PC, address construction, value source, and
immediate callers/guards. No writer selects immutable; a direct controller,
timer/demo, or state source selects its matching hypothesis; any unresolved
writer keeps the boundary hypothesis open.

Exact commands:

```sh
rg -n -B 16 -A 20 '0x800D2BFC|0X800D2BFC|0x2BFC|0X2BFC|0x2C00|0X2C00' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1800
rg -n -B 16 -A 20 'MEM_[BHW]\([^)]*0x2BFC|MEM_[BHW]\([^)]*0X2BFC|MEM_[BHW]\([^)]*0x2C00|MEM_[BHW]\([^)]*0X2C00' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1800
rg -n -B 12 -A 18 'getController(New|Raw)|timer|demo|attract|menu|asset|save|ship|cutscene' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1200
```

Expected output is one complete generated-tree writer/caller table for the
selected table range, with a selected hypothesis or an explicitly unresolved
writer boundary. No build or runtime run is needed.
