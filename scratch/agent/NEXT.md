# NEXT work unit (s1049)

HYPOTHESIS-ID: retail-state-transition-input

Perform one bounded static audit of the writers that can set
`gGameSettings+0x20` and the menu state halfword at `0x800CFF50`. Do not run
the game or arm a freelist watch. Trace only the callers/branches that can
enable the width-320 menu loop or set table index 0 before the
`0x800C5A5C` dispatch.

## Competing hypotheses and discriminator

* `H-retail-state-writer-input`: an input edge/mask directly writes either
  `gGameSettings+0x20` or `0x800CFF50=0`.
* `H-retail-state-writer-timer`: a timer, attract counter, or demo predicate
  writes one of those fields without an input gate.
* `H-retail-state-writer-upstream`: the fields are only copied from another
  persistent state object; the missing transition is upstream of this menu
  overlay.

Discriminating measurement: produce one writer table listing every generated
store/copy into `gGameSettings+0x20` and `0x800CFF50`, its guarding predicates,
and its caller. A direct input mask selects the input-writer hypothesis; a
timer/demo-only guard selects the timing-writer hypothesis; only upstream
copy sources with no local decision select the upstream-writer hypothesis.

## Exact commands

```sh
rg -n -C 4 "0x800CFF50|800CFF50|gGameSettings|D_80130B40|0x20\(.*s[0-9]+\)|demoStep|demoInputs" syms docs /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs 2>/dev/null | head -400
rg -n -C 5 "sh[[:space:]]+.*0x20|MEM_H\(0X20|MEM_W\(0X20|0x800CFF50|800CFF50" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c 2>/dev/null | head -400
rg -n -C 3 "getControllerNewButtonsPressed|demoStep|demoInputs|0x80109AE0|0x8010BCA0" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c syms docs 2>/dev/null | head -300
```

Expected output is one bounded table with ROM/guest addresses and a selected
hypothesis. No build is needed unless the audit finds an existing source probe
that cannot be interpreted statically.
