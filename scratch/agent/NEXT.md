# NEXT work unit (s1050)

HYPOTHESIS-ID: retail-state-transition-input

Perform one bounded static audit of pointer-mediated copies into
`gGameSettings+0x20` (`0x80130B60`) and the callers that can select table index
0 at `menuOverlayInit`. Do not run the game or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-retail-copy-input`: a caller reads controller edge/mask data, then copies
  or writes the menu-enable byte/state.
* `H-retail-copy-timer`: the copy is guarded only by timer/demo/attract state.
* `H-retail-copy-upstream`: the values arrive from a persistent state object or
  return value, with no local input/timer decision.

Discriminating measurement: produce one table of every callsite that passes a
pointer to `gGameSettings`, every store/copy at offset `0x20`, and every
index-0 selection branch, including the nearest guard and caller. An input
mask selects the input-copy hypothesis; timer/demo-only guards select the
timer-copy hypothesis; source-object copies with no local decision select the
upstream-copy hypothesis.

Exact commands:

```sh
rg -n -B 8 -A 12 "0x80130B40|0XB40|0xB40|MEM_[HWB]\\(0X20|800C5A84|case 0" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -800
rg -n -C 5 "getControllerNewButtonsPressed|demoStep|demoInputs|0x80109AE0|0x8010BCA0|0x800C5A5C|0x800A75C0" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -500
```

Expected output is one bounded writer/caller table and a selected hypothesis.
No build or runtime run is needed unless the static table exposes an existing
probe whose semantics cannot be read from generated code.
