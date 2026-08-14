# NEXT work unit (s1047)

HYPOTHESIS-ID: retail-state-transition-input

Perform one bounded static audit of the retail ROM/decomp state transition
that should turn the verified Start input into the documented 512 hangar
phase. Do not run the game or arm a freelist watch. Start from the known
width-320 attract state and enumerate the game's input reads and state writes
around the transition; do not guess another button schedule.

## Competing hypotheses and discriminator

* `H-retail-start-gate`: the transition requires a Start edge/state bit that
  the current PIF-positive recipe does not satisfy because the game samples a
  different input structure or edge condition.
* `H-retail-other-input`: a distinct required button or held input is read by
  the transition code; Start-only and Start+Z do not exercise it.
* `H-retail-timing-state`: the input contract is sufficient, but a timer,
  attract counter, or persistent state gate blocks the transition independently
  of button identity.

Discriminating measurement: produce a source/ROM-address table for the
width-320 attract transition showing every input read, edge/hold test, and
timer/state predicate on the path to the 512 hangar state. A Start/edge read
that is absent or mismatched selects `H-retail-start-gate`; a separate button
read selects `H-retail-other-input`; only timer/state predicates with no
missing input read select `H-retail-timing-state`.

## Exact commands

```sh
rg -n -C 4 "0x006dd280|0x6ab400|0x6ab800|512|Start|start|attract|hangar|PIF|controller|pad" tools/oracle/README.md docs/PROJECT-OVERVIEW.md docs/CURRENT-TRUTH.md
rg -n -C 3 "80128|80129|8012A|input|pad|button|START|start" syms tools N64Recomp 2>/dev/null | head -240
rg -n "0x006dd280|0x006ab|0x00690|512|hangar|attract" docs tools src RecompiledFuncs 2>/dev/null | head -240
```

Expected output is one bounded table with ROM/guest addresses and a selected
hypothesis. No build is needed unless the audit finds an existing source
probe that cannot be interpreted statically.
