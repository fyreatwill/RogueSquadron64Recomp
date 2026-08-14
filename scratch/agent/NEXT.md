# NEXT work unit (s1059)

HYPOTHESIS-ID: retail-state-transition-input

Perform one bounded static audit of the two ordinary return data words selected
by `runHangarSelectionFrame`: enumerate all generated stores whose effective
addresses are `0x800CD6D4` and `0x800CD6D0` (the `0x800D:0xFFFFD6D4` and
`0x800D:0xFFFFD6D0` notation used in the ledger), then inspect the immediate
callers of any unresolved producer. Do not build, run the game, or arm a
freelist watch.

Competing hypotheses and discriminator:

* `H-frame-word-input`: a direct writer or its immediate caller reads a
  controller edge or button mask.
* `H-frame-word-demo`: a direct writer or its immediate caller reads a timer,
  attract, or demo counter.
* `H-frame-word-state`: all classified writers are driven by ship/menu/asset or
  persistent state, with no local input/timer/demo source.
* `H-frame-word-boundary`: one or both words have no generated direct writer or
  the producer is behind an unresolved helper, so classification must remain
  open.

Discriminating measurement: produce one complete table with writer PC,
effective address calculation, width, value source, and immediate caller for
both words. Any direct controller source selects input; any direct timer/demo
source selects demo; only state-shaped writers select state. A missing writer
or unresolved helper selects the boundary hypothesis and must not be inferred.

Exact commands:

```sh
rg -n -B 8 -A 12 '0x800CD6D4|0x800CD6D0|FFFFD6D4|FFFFD6D0' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -B 6 -A 10 'lui.*0x800D|addiu.*-0x292C|addiu.*-0x292[CD]|sw.*-0x292C|sw.*-0x2930' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -B 14 -A 20 'getControllerNewButtonsPressed|timer|demo|attract|0x800CD6D4|0x800CD6D0' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -600
```

Expected output is one complete writer/caller table and a selected hypothesis
or explicitly unresolved producer boundary. No build or runtime run is needed.
