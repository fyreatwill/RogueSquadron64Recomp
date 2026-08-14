# NEXT work unit (s1066)

HYPOTHESIS-ID: retail-selector-upstream-state

Perform one bounded static audit of every generated call site of
`cycleIdleDemoId` (`0x8006F07C`), the only exact writer of the selector source
byte `0x80130B54`. Classify each caller's immediate guard and argument/state
inputs, and determine whether the selector update is driven directly by
controller input, a timer/demo/attract path, or persistent menu/setup state.
Do not build, run the game, or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-cycle-input`: at least one caller has a direct controller edge/mask input.
* `H-cycle-demo`: callers are reached through timer/demo/attract scheduling.
* `H-cycle-state`: all callers are setup/menu/state driven with no direct input
  or timer/demo predicate.
* `H-cycle-boundary`: a call target or caller input remains outside generated
  code and cannot be classified.

Discriminating measurement: produce one complete call-site table listing each
`jal cycleIdleDemoId` address, its immediate branch predicates, argument/state
sources, and caller chain. A direct controller predicate selects
`H-cycle-input`; a timer/demo/attract predicate with no input selects
`H-cycle-demo`; state-only callers select `H-cycle-state`; unresolved calls
keep `H-cycle-boundary` open.

Exact commands:

```sh
rg -n -B 24 -A 30 'cycleIdleDemoId\(rdram, ctx\)|jal.*0x8006F07C|0x8006F07C' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -B 18 -A 24 'getController(New|Raw)|0x8013A9|0x80130B54|timer|demo|attract|idle|cycleIdleDemoId' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1800
rg -n -B 8 -A 12 'cycleIdleDemoId' /Users/williambuckley/Documents/Tools/rogue_squadron64 2>/dev/null | head -500
```

Expected output is one complete caller/input table with a selected
hypothesis or an explicitly unresolved boundary. No build or runtime run is
needed.
