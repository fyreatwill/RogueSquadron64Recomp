# Next: bounded generated-symbol audit for `func_800927B0`

The M4 boundary is parked after Session 5335: both controls were live, but
the retail and port PC/origin key domains did not align. Do not normalize those
keys or infer a VACC writer. Resume the generated-symbol campaign instead.

Competing hypotheses and discriminator:

- H1: the companion decomp/map, generated body span, and live callers identify
  one stable human name; a regeneration-safe rename is justified.
- H2: the candidate is a false split, data/host-wrapper artifact, or has no
  semantic companion evidence; retain `func_800927B0`.
- H3: source/body/caller boundaries disagree, so the candidate needs a
  separate boundary audit before either naming decision.

Discriminating measurement: in one bounded audit, compare the candidate's
exact generated span and callers with the companion symbol/decomp map and
record whether all three boundaries agree. H1 requires agreement plus a
semantic name; H2 requires a clean absence of such a name with agreeing
boundaries; H3 requires a span/caller disagreement. Do not rename on an
address-only match.

Commands:

```sh
rg -n "func_800927B0|800927B0" RecompiledFuncs docs tools /Users/williambuckley/Documents/Tools/rogue_squadron64 2>/dev/null
grep -n "func_800927B0" PORTING-STATE.md | tail -20
```

If H1 is selected, update the existing fixup/mapping source and verify the
generated/header references; otherwise make only the audit record. No runtime
instrument or mitigation is authorized by this unit.

HYPOTHESIS-ID: generated-symbol-renaming-sweep
