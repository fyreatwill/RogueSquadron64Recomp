# NEXT work unit (s1065)

HYPOTHESIS-ID: retail-selector-upstream-state

Perform one bounded static audit of the unresolved initialization boundary for
`dLevelByDemoId` at `0x800CD404`: inspect the linked data definition and its
ROM/section ownership, then classify whether the table is initialized from
immutable ROM data or copied/populated by a generated/runtime path. Do not
build, run the game, or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-table-ROM`: the data symbol is loaded as immutable section/ROM content.
* `H-table-copy`: a generated or runtime copy populates the table.
* `H-table-boundary`: ownership remains unresolved outside generated code.

Discriminating measurement: produce one data/section ownership table containing
symbol address, section/ROM range, all references, and any population call.
ROM-backed immutable ownership selects `H-table-ROM`; a copy/population site
selects `H-table-copy`; missing ownership keeps `H-table-boundary` open.

Exact commands:

```sh
rg -n -B 16 -A 20 '0x800D2BFC|0X800D2BFC|0x2BFC|0X2BFC|0x2C00|0X2C00' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1800
rg -n -B 16 -A 20 'MEM_[BHW]\([^)]*0x2BFC|MEM_[BHW]\([^)]*0X2BFC|MEM_[BHW]\([^)]*0x2C00|MEM_[BHW]\([^)]*0X2C00' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1800
rg -n -B 12 -A 18 'getController(New|Raw)|timer|demo|attract|menu|asset|save|ship|cutscene' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1200
```

Expected output is one complete data-ownership table with a selected hypothesis
or an explicitly unresolved boundary. No build or runtime run is needed.
