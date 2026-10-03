# Next work unit: bounded generated-symbol renaming lead

HYPOTHESIS-ID: generated-symbol-renaming-sweep

M5 is parked pending a new arm-stability discriminator. The `rs_zcfree`
incoming-`$a0` M3 class was closed at static scope in s3790 with no guard
justified. The next unit is one bounded, regeneration-safe symbol-renaming
lead from the human-mapped decomp symbols, not a runtime experiment.

Competing hypotheses and discriminator for the lead:

- H1: the selected placeholder functions have an unambiguous human mapping
  from the companion symbol/decomp material; rename only those exact symbols.
- H2: mappings are ambiguous or semantics are not visible; preserve the
  placeholders and record the unresolved sites.
- H3: the selected region is already named or outside the current generated
  tree; select no rename and move to the next ranked lead.

The discriminating measurement is a bounded table of every selected placeholder
in the chosen region, joined against companion symbol names and call/string
evidence. A rename is accepted only for an exact one-to-one mapping; the
result must either change the mapping source or produce a new bounded census.

Exact preflight commands:

    grep -n '^## Session ' PORTING-STATE.md | tail -15
    rg -n 'func_0x|func_[0-9A-Fa-f]{8}' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -200
    rg -n '0x8000[0-9A-Fa-f]{4}|func_[0-9A-Fa-f]{8}' docs/game-architecture.md /Users/williambuckley/Documents/Tools/N64Recomp/rogue_squadron64 2>/dev/null | head -200

Choose one contiguous, bounded lead from the census, update the existing
rename mapping/fixup source if and only if the mapping is exact, and verify
that no generated C file is hand-edited. Do not build unless the mapping
pipeline requires it; do not start a second region in the same iteration.
