# NEXT work unit (s1080)

HYPOTHESIS-ID: oracle-512-state-gate-owner

Run exactly one bounded static audit of the `mainGameLoop` state/asset gate at
`0x8003E07C`. Identify the backing address/object for the byte read using the
register setup in `funcs_8.c`, enumerate all generated and companion/non-
generated writers, and classify the initialization path that can leave it zero
before the width-320 attract loop. Do not build, run the oracle, change the
input schedule, or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-gate-writer`: the gate's backing byte and a concrete writer/initializer are
  found; its zero value explains why `menuOverlayInit` is not entered.
* `H-gate-alias`: the generated address is clear but only pointer/alias or raw
  guest writes can reach it; ownership remains outside the typed census.
* `H-audit-open`: the backing address or complete writer set cannot be
  established from the available generated/companion sources.

Discriminating measurement: a concrete backing address plus writer selects
`H-gate-writer`; a complete address with only pointer/raw ownership selects
`H-gate-alias`; an incomplete address/writer table selects `H-audit-open`.
Before any build, run:

```sh
rg -n -S '8003E07C|80130B|gGameSettings|menuOverlayInit' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs patches src docs scratch tools --glob '*.{c,h,cpp,md,txt,sh}'
rg -n -S '8003E07C|80130B|gGameSettings|menuOverlayInit' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 --glob '*.{c,h,txt,s}'
```
