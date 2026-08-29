# NEXT work unit — decode the local retail VI consumer body

HYPOTHESIS-ID: m5-retail-elf-boundary

## Single work unit

Use the locally available non-stripped companion ELF to recover the
instruction-level body of `osViSetMode` and `__osViSwapContext`, then identify
the pending-to-descriptor or descriptor-to-origin store edge not already
watched.

## Competing hypotheses

- `H-ELFExposesNewEdge`: the ELF body contains a not-yet-watched transition
  edge, which can be phase-keyed in the retail oracle.
- `H-ELFOnlyConfirmsKnownEdge`: the body contains only already-watched
  publication instructions, so the missing writer lies elsewhere.
- `H-ELFArtifactMismatch`: the ELF does not match the USA v1.0 retail image or
  lacks usable code bytes, so it cannot ground a new watch.

## Discriminating measurement

The decoded function ranges must match the symbol addresses/sizes and expose
at least one instruction that writes or transfers the active VI descriptor or
origin. One oracle run must arm a whole-RDRAM write positive control plus the
new edge and title `1024`/hangar `512` phase controls. A target-phase hit on a
new edge selects `H-ELFExposesNewEdge`; only known-edge hits select
`H-ELFOnlyConfirmsKnownEdge`; an address/byte mismatch selects
`H-ELFArtifactMismatch`.

## Exact local inputs

```sh
file /Users/williambuckley/Documents/Tools/rogue_squadron64/build/roguesquadron.elf
nm -S -n /Users/williambuckley/Documents/Tools/rogue_squadron64/build/roguesquadron.elf
```

Do not change audio or port behavior until the oracle measurement selects an
edge.
