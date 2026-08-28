# NEXT work unit (s2928) — bounded generated-symbol reconciliation after 0x80069AF0

HYPOTHESIS-ID: generated-symbol-renaming-sweep

The M5 route discriminator remains paused as route-invalid, M3 is parked, and
the s2927 M4 revisit already resolved its static register-lifetime question.
Inspect the next remaining placeholder after `0x80069AF0` as one bounded
source-backed rename/data-gap classification. Do not add runtime probes or
change behavior.

## Competing hypotheses and discriminator

- H-CallableSemantic: the candidate is a real callable function and companion
  or m2c evidence supplies a semantic name; rename only to that exact name.
- H-DataGap: it is a mechanically non-callable split/fixup fragment with no
  callers or independent lookup; rename to `data_gap_<address>` in every
  regeneration-safe map/source surface.
- H-Ambiguous: valid instructions or incomplete boundaries leave callability
  unresolved; preserve the placeholder and record why.

The discriminator is a complete bounded table for every placeholder in the
next interval after `0x80069AF0`: address/size, generated body, predecessor and
successor boundaries, companion/m2c name, generated callers/lookups, and
whether a callable prologue/return or invalid-data filler is present. A
semantic companion match selects H-CallableSemantic; a proven non-callable
record with no callers selects H-DataGap; otherwise H-Ambiguous.

## Exact commands

```sh
rg -n 'fake_func_8006|func_8006' syms tools/rename build/factor5_ucode
sed -n '<bounded generated interval>' build/factor5_ucode/factor5_ucode_recompiled.c
```

Record the complete table at
`scratch/agent/s2928_generated_symbol_rename/source-table.md`. No game run is
needed unless a regeneration mismatch is discovered.
