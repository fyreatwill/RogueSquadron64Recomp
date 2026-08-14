# NEXT work unit (s1051)

HYPOTHESIS-ID: retail-state-transition-input

Perform one bounded static audit of the actual `menuOverlayInit` selector state
at `0x800CCF50` (`0x800D-0xB0`): enumerate every writer of its halfword and
every caller/state transition that can produce selector index 0. Do not run
the game or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-selector-input`: selector writes are driven by controller edge/mask data.
* `H-selector-demo`: selector writes are driven by timer/demo/attract state.
* `H-selector-upstream`: selector writes come from a persistent state or return
  value without a local input/timer decision.

Discriminating measurement: produce one table of every store/copy to physical
`0x800CCF50`, every read feeding the `0..10` jump-table index, and every caller
or guard immediately around those sites. An input mask selects
`H-selector-input`; timer/demo-only guards select `H-selector-demo`; source or
return-value writes with no local decision select `H-selector-upstream`.

Exact commands:

```sh
rg -n -B 10 -A 12 "0x800CCF50|0X800D|0XB0|MEM_[HWB]\\(-0XB0|menuOverlayInit" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -800
rg -n -C 6 "getControllerNewButtonsPressed|demoStep|demoInputs|800CCF50|800C5A5C|800A75C0|menuOverlayInit" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -600
```

Expected output is one bounded writer/caller table and a selected hypothesis,
or an explicit no-writer result. No build or runtime run is needed unless the
static table exposes an existing probe whose semantics cannot be read from
generated code.
