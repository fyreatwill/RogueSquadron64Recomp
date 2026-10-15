# Next work unit

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Revisit the generated-symbol sweep only after a new generated snapshot or
companion mapping source is available. The s4888 audit found no safe candidate:
`func_8000040C` has no companion semantic mapping, and `func_800E9AE0` is an
intentional companion placeholder with no generated caller because of a
documented false split reference. Do not rename either one.

Competing hypotheses:
- H1: a future placeholder has companion mapping, live body/callers, and exact
  adjacent/TOML span agreement; one rename is safe.
- H2: candidates exist but fail one of those gates; leave them unchanged.
- H3: the external generated snapshot or companion mapping remains unavailable;
  record the concrete path/tool blocker.

Discriminator: independently verify all three H1 gates for one candidate. H1
authorizes one bounded mapping edit; H2 parks the candidate; H3 records the
falsifiable availability failure.

Exact commands:

    env RSR_FUNCS_DIR=/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs python3 tools/rename/find_state_machines.py
    env RSR_FUNCS_DIR=/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs python3 tools/rename/find_callers.py <candidate>
    rg -n '<candidate-address>|<candidate-name>' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs

Expected outcomes: one candidate passes all three gates and receives one
mapping edit; candidates fail a gate and remain unchanged; or the required
external source/tool is unavailable and the blocker is recorded. Do not build
or regenerate for this unit.
