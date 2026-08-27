# NEXT work unit (s2798) — repair the generated 0x80101CCC data-gap rename

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

The previous sweep renamed the companion's four-byte fake/data entry at
`0x80101CCC` to the name of the following real function, creating duplicate
`lv2_initializeObjectTracking` declarations/definitions. Correct that
generated-symbol batch by naming the non-callable entry
`data_gap_80101CCC`, and update the rename map so the correction survives the
next generated-symbol reconciliation. Do not alter the real function at
`0x80101CD0`.

## Competing hypotheses and discriminator

- H-data-gap: `0x80101CCC` is the companion's explicit four-byte fake/data
  entry, so a mechanical `data_gap_80101CCC` name removes the collision.
- H-real-function: the four-byte entry is actually part of the following
  callable function, so renaming it would damage dispatch and the duplicate
  should instead be handled by regeneration metadata.
- H-stale-generated: only checked-in generated output is stale; updating the
  output without the rename map would let the duplicate return on the next
  sweep.

The discriminator is the same-build symbol/build check: the companion size
and name at `0x80101CCC`, exactly one declaration/definition of
`lv2_initializeObjectTracking`, exactly one data-gap entry, and a successful
`RecompiledFuncs`/Debug compile. A duplicate after the map update selects
H-stale-generated; a clean compile with the real function still at
`0x80101CD0` selects H-data-gap; altered dispatch/body bytes select
H-real-function.

## Exact commands

```sh
  rg -n "80101CCC|lv2_initializeObjectTracking|data_gap_80101CCC" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/{funcs.h,funcs_43.c,recomp_overlays.inl}
  cmake --build build --config Debug --target RecompiledFuncs -j
  git diff --check
```
