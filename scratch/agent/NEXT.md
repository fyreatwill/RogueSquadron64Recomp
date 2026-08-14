# NEXT work unit (s954)

Pre-run decision: source-only audit of the eight indirect call sites in the
72 direct callers; do not build, run, enqueue a soak, or land a guard.

HYPOTHESIS-ID: m3-slotdispatcheriter-stacksp-class

The 144 direct `slotDispatcherIter` callers are frame-balanced in generated
source, with no non-frame assignment to `ctx->r29`. Eight enclosing callers
still contain `LOOKUP_FUNC`/`jalr` calls whose target behavior could mutate the
shared context before the dispatcher call.

Competing hypotheses:

- H-slotdispatcheriter-stacksp-indirect-corruption: an indirect target writes
  or fails to restore the shared guest `$sp`.
- H-slotdispatcheriter-stacksp-indirect-balanced: all indirect targets
  preserve the context, leaving no caller-side writer.
- H-slotdispatcheriter-stacksp-stub-artifact: an indirect target is a known
  degenerate stub and is the corruption origin.
- H-slotdispatcheriter-stacksp-unclassified: target provenance or mutation
  remains unresolved.

Discriminating measurement: enumerate the eight indirect target addresses and
their target bodies, inspect every `ctx->r29` write/restore, and cross-check
target names/addresses against `funcs.h` and
`../rogue_squadron64/symbol_files/main_overlay.txt`. An incorrect target-side
`$sp` write selects indirect-corruption; balanced targets select
indirect-balanced; a known stub target selects stub-artifact; unresolved
provenance selects unclassified.

Exact starting commands:

`rg -n "LOOKUP_FUNC|jalr" ../N64Recomp/RecompiledFuncs/funcs_*.c`

`rg -n -F "slotDispatcherIter(rdram, ctx);" ../N64Recomp/RecompiledFuncs/funcs_*.c`

`rg -n "ctx->r29\\s*=" ../N64Recomp/RecompiledFuncs/funcs_*.c`

Cross-check every target address against `funcs.h` and the companion map.
