# NEXT work unit (s1048)

HYPOTHESIS-ID: retail-state-transition-input

Perform one bounded static audit of the width-320 attract state's actual
caller and state writer around the table dispatch at `0x800C5A5C`. Do not run
the game or arm a freelist watch. Trace only the caller chain that selects the
state-table index and the writes that could enter the `0x800C6854` hangar
handoff; do not guess another button schedule.

## Competing hypotheses and discriminator

* `H-retail-start-gate`: the width-320 caller reads a Start edge or Start bit
  and writes the hangar-selecting state when it is present.
* `H-retail-other-input`: the caller requires a different button or composite
  mask before writing that state.
* `H-retail-timing-state`: the caller has no missing input read, but a timer,
  attract counter, or persistent state predicate prevents the state write.

Discriminating measurement: produce one caller/state table from the width-320
function to the `0x800C5A5C` jump table, listing every input read, mask,
timer/attract predicate, and state write. A Start predicate selects
`H-retail-start-gate`; another button/composite mask selects
`H-retail-other-input`; only non-input predicates with a complete input path
selects `H-retail-timing-state`.

## Exact commands

```sh
rg -n -C 4 "0x800C5A5C|0x800C6854|0x006dd280|0x6ab400|0x6ab800|512|attract|hangar" docs tools syms
rg -n -C 5 "800C5A5C|800C6854|state-0xB0|D_8013A960|getControllerNewButtonsPressed" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs 2>/dev/null | head -300
rg -n -C 3 "0x800C5A5C|0x800C6854|0x80109AE0|demoStep|demoInputs" syms docs /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs 2>/dev/null | head -300
```

Expected output is one bounded table with ROM/guest addresses and a selected
hypothesis. No build is needed unless the audit finds an existing source probe
that cannot be interpreted statically.
