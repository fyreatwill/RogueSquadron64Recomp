# NEXT work unit (s1052)

HYPOTHESIS-ID: retail-state-transition-input

Perform one bounded static audit of the upstream state passed by `mainGameLoop`
to `menuOverlayInit`: trace the eight call sites' constant `a1` selectors and
the guards/data that choose those call sites. Do not run the game or arm a
freelist watch.

Competing hypotheses and discriminator:

* `H-caller-input`: a caller selection is guarded by controller edge/mask data.
* `H-caller-demo`: a caller selection is guarded by timer/demo/attract state.
* `H-caller-state`: a caller selection follows persistent state, asset flags, or
  a return value without a local input/timer decision.

Discriminating measurement: produce one table for all eight `mainGameLoop`
call sites showing the selector constant, the immediately preceding branch/data
source, and any controller/timer/demo read. A controller mask selects
`H-caller-input`; timer/demo-only state selects `H-caller-demo`; persistent
state/return/asset data with no local input decision selects `H-caller-state`.

Exact commands:

```sh
rg -n -B 18 -A 12 "LOOKUP_FUNC\\(0x800C58A0\\)|jal +0x800C58A0|menuOverlayInit" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -1000
rg -n -B 10 -A 14 "getControllerNewButtonsPressed|demoStep|demoInputs|timer|8003E0|mainGameLoop" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_8.c | head -1000
```

Expected output is one bounded caller/guard table and a selected hypothesis,
or an explicit unresolved source. No build or runtime run is needed unless the
static table exposes an existing probe whose semantics cannot be read from
generated code.
