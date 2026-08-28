# NEXT work unit (s2942) — bounded generated-symbol classification at 0x80099C4C

HYPOTHESIS-ID: generated-symbol-renaming-sweep

M5 remains route-gated, M3 is parked, and the s2927 M4 revisit resolved its
static register-lifetime question. Inspect `0x80099C4C`, the next remaining
placeholder after the reconciled streamed-voice frame fragment, as one bounded
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

The discriminator is a complete bounded table for `0x80099C4C`: address/size,
generated body, predecessor and successor boundaries, companion/m2c name,
generated callers/lookups, and whether a callable prologue/return or invalid
data filler is present. A semantic companion match selects H-CallableSemantic;
a proven non-callable record with no callers selects H-DataGap; otherwise
H-Ambiguous.

## Exact commands

```sh
rg -n 'fake_func_80099C4C|func_80099C4C|80099C4C' syms tools ../N64Recomp/RecompiledFuncs ../rogue_squadron64/symbol_files
rg -n -C 12 'fake_func_80099C4C|func_80099C4C|80099C4C' ../N64Recomp/RecompiledFuncs/funcs_*.c
```

Record the complete table at
`scratch/agent/s2942_generated_symbol_rename/source-table.md`. No game run is
needed unless a regeneration mismatch is discovered.
