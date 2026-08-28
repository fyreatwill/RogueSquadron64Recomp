# NEXT work unit (s2930) — bounded generated-symbol reconciliation at 0x8007A86C

HYPOTHESIS-ID: generated-symbol-renaming-sweep

The M5 route discriminator remains paused as route-invalid, M3 is parked, and
the s2927 M4 revisit already resolved its static register-lifetime question.
Inspect `0x8007A86C`, the next placeholder after the reconciled
`0x80072CE8`, as one bounded source-backed rename/data-gap classification.
There is an older s2874 inspection of this address; re-check it only under the
current complete discriminator and do not add runtime probes or change
behavior.

## Competing hypotheses and discriminator

- H-CallableSemantic: the candidate is a real callable function and companion
  or m2c evidence supplies a semantic name; rename only to that exact name.
- H-DataGap: it is a mechanically non-callable split/fixup fragment with no
  callers or independent lookup; rename to `data_gap_<address>` in every
  regeneration-safe map/source surface.
- H-Ambiguous: valid instructions or incomplete boundaries leave callability
  unresolved; preserve the placeholder and record why.

The discriminator is a complete bounded table for `0x8007A86C`: address/size,
generated body, predecessor and successor boundaries, companion/m2c name,
generated callers/lookups, and whether a callable prologue/return or
invalid-data filler is present. A semantic companion match selects
H-CallableSemantic; a proven non-callable record with no callers selects
H-DataGap; otherwise H-Ambiguous.

## Exact commands

```sh
rg -n 'fake_func_8007A86C|func_8007A86C|8007A86C' syms tools/rename ../N64Recomp/RecompiledFuncs ../rogue_squadron64/symbol_files
rg -n -C 12 'fake_func_8007A86C' ../N64Recomp/RecompiledFuncs/funcs_*.c
```

Record the complete table at
`scratch/agent/s2930_generated_symbol_rename/source-table.md`. No game run is
needed unless a regeneration mismatch is discovered.
