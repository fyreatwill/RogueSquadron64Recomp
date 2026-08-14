# NEXT work unit (s1068)

HYPOTHESIS-ID: retail-selector-field-aliases

Perform one bounded static audit of every generated store that can alias the
selector field at `0x80130B54` (`0x80130B40 + 0x14`), including wider stores
whose byte lanes overlap it and computed-base stores missed by an exact literal
search. Classify each writer's value source and caller chain.

Competing hypotheses and discriminator:

* `H-alias-input`: an overlapping/computed writer receives a direct controller edge or mask.
* `H-alias-demo`: an overlapping/computed writer is timer/demo/attract driven.
* `H-alias-state`: every generated alias is setup/menu/state shaped.
* `H-alias-boundary`: a candidate writer or its base remains outside generated code.

Discriminating measurement: produce one complete writer table listing every
exact, overlapping, and computed-base store candidate, byte lane, value
expression, immediate predicates, and caller chain. A direct input predicate
selects `H-alias-input`; timer/demo/attract selects `H-alias-demo`; state-only
writers select `H-alias-state`; unresolved base/value ownership keeps
`H-alias-boundary` open.

Exact commands:

```sh
rg -n -B 8 -A 12 '0x80130B54|0x80130B40|0x14\(.*8013|cycleIdleDemoId' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -B 18 -A 24 'sb|sh|sw|sd|MEM_[BHW]|getController(New|Raw)|timer|demo|attract|idle' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -2200
rg -n -B 8 -A 12 '0x80130B54|cycleIdleDemoId|demoId' /Users/williambuckley/Documents/Tools/rogue_squadron64 2>/dev/null | head -600
```

No build or runtime run is needed.
