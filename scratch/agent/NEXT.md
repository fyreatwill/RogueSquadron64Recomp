# NEXT work unit (s1160)

HYPOTHESIS-ID: post640-vi-callpath-census

Perform one bounded static census of the complete generated VI call path after
the s1159 H3 result. Enumerate every generated `osViSetMode_recomp` callsite
and the sole generated `selectAndApplyViMode` caller. For each, record guest
address, containing function, mode-pointer setup, and whether its control flow
can follow `applyPendingViChanges` at `0x80019914`.

Competing hypotheses and discriminator:

- H1: the observed `0x80128DF0` request is reached only through
  `selectAndApplyViMode`.
- H2: the selector consumer is reached through a different generated edge, but
  its logged entry was missed by an instrumentation placement defect.
- H3: a direct generated VI caller independently produces `0x80128DF0`,
  explaining the host request while the selector consumer remains absent.

The discriminating measurement is one exhaustive callsite table: every
generated `osViSetMode_recomp` edge, its mode pointer/width setup, and its
caller relationship to `applyPendingViChanges` and `selectAndApplyViMode`.
H1/H2 leaves no independent owner; H3 identifies one. This is a static unit,
so no build or run is authorized unless the census exposes an unresolved
duplicate live edge.

Commands:

    rg -n "osViSetMode_recomp\\(|selectAndApplyViMode\\(" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
    sed -n '29990,30110p' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c
    sed -n '5200,5450p' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_5.c

Expected outcomes: H1 closes the independent-path hypothesis; H2 requires an
instrumentation-placement audit; H3 identifies the direct generated owner and
closes the selector-consumer boundary. Do not infer parser or renderer
causality from this VI call-path result.
