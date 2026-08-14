# NEXT work unit (s1067)

HYPOTHESIS-ID: retail-selector-upstream-state

Perform one bounded static audit of every generated caller of the selector
clear form at `0x8006F0AC` (the generated `cycleIdleDemoId` return/clear path).
Classify each caller's immediate guard and caller-chain state source, and
determine whether the clear is setup/menu-state driven, timer/demo/attract
driven, controller-driven, or outside generated code.

Competing hypotheses and discriminator:

* `H-clear-input`: at least one caller is gated by a direct controller edge or mask.
* `H-clear-demo`: at least one caller is reached by timer/demo/attract scheduling.
* `H-clear-state`: all generated callers are setup/menu/state driven with no direct input or timer/demo predicate.
* `H-clear-boundary`: a target, caller, or source remains outside generated code.

Discriminating measurement: produce one complete call-site table listing each
`jal 0x8006F0AC` address, immediate branch predicates, argument/state sources,
and caller chain. A direct controller predicate selects `H-clear-input`; a
timer/demo/attract predicate selects `H-clear-demo`; state-only callers select
`H-clear-state`; unresolved calls keep `H-clear-boundary` open.

Exact commands:

```sh
rg -n -B 24 -A 30 'cycleIdleDemoId|0x8006F0AC|jal.*0x8006F0AC' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -B 18 -A 24 'getController(New|Raw)|0x80130B54|0x8006F0AC|timer|demo|attract|idle' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1800
rg -n -B 8 -A 12 '0x8006F0AC|cycleIdleDemoId' /Users/williambuckley/Documents/Tools/rogue_squadron64 2>/dev/null | head -500
```

No build or runtime run is needed.
