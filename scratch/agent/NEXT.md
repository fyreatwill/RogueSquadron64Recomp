# NEXT work unit (s1056)

HYPOTHESIS-ID: retail-state-transition-input

Perform one bounded static audit of the selector-0 writers inside
`menuOverlayInit`: enumerate every generated store of zero to
`0x800CFF50` (`-0xB0($s1)`) and trace each branch's immediate predicate and
nearest state producer. Do not build, run the game, or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-selector0-input`: at least one zero-writing branch is controlled by a
  controller edge or button-mask source.
* `H-selector0-demo`: at least one zero-writing branch is controlled by a
  timer, attract, or demo counter source.
* `H-selector0-state`: all zero-writing branches are controlled by persistent,
  asset, unlock, return-value, or other menu state with no local input/timer
  source.

Discriminating measurement: produce one complete table of every
`MEM_H(-0xB0, ...) = 0` site in `menuOverlayInit`, including its branch
predicate, immediate data source, and nearest producer. Any controller source
selects `H-selector0-input`; any timer/demo source selects `H-selector0-demo`;
if all rows are state/asset/unlock/return-value sources, select
`H-selector0-state`. A missing exact store is itself a boundary result and
must be reported rather than inferred from the case-0 return.

Exact commands:

```sh
rg -n -B 18 -A 24 'MEM_H\(-0XB0|sh[[:space:]]+\$[^,]+, -0xB0\(\$s1\)|0x800CFF50' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_34.c
rg -n -B 14 -A 18 'getControllerNewButtonsPressed|timer|demo|attract|isUnlockBitSet|MEM_H\(-0XB0' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_34.c | head -1200
```

Expected output is one complete selector-0 writer table and a selected
hypothesis or an explicitly unresolved producer boundary. No build or runtime
run is needed.
