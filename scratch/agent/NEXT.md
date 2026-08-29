# NEXT work unit — rename a defensible generated-symbol batch

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Select one bounded batch of placeholder `func_0x...` symbols from the
external generated snapshot and rename only entries with a human mapping
supported by the companion decomp symbols/m2c output or an unambiguous
call/data-flow match. Do not rename the two deliberately preserved
`fake_func_*` fragments or invent semantic names. This is a source-only
cleanup; no build or game run is required.

## Competing hypotheses

- H-DefensibleBatch: at least one placeholder has an independently supported
  human name and can be renamed consistently across generated C/header/symbol
  references.
- H-AmbiguousBatch: the candidate batch has no support beyond address-shaped
  evidence, so it must remain unchanged and the next batch must be selected.
- H-ExternalSnapshotUnavailable: the generated snapshot or companion mapping
  is unavailable in this checkout, so this unit must be substituted only with
  a documented, falsifiable blocker.

## Discriminating measurement

The discriminating measurement is a mapping table for every selected symbol:
generated address, proposed human name, companion/decomp evidence, and all
reference sites. One supported mapping selects H-DefensibleBatch; a complete
batch with no supported mapping selects H-AmbiguousBatch; absent input files
selects H-ExternalSnapshotUnavailable. The falsifier for the unavailable
snapshot explanation is a readable generated file plus a matching companion
symbol/m2c record.

## Exact command

```sh
find /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs -maxdepth 1 -type f -name 'funcs_*.c' -print
rg -n '\bfunc_[0-9A-Fa-f]{8}\b' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
find /Users/williambuckley/Documents/Tools -maxdepth 3 -type d -name 'rogue_squadron64' -print
```

If H-DefensibleBatch is selected, the next iteration should apply the next
bounded rename batch and verify generated references/build inputs. If the
snapshot is unavailable, restore/provide it before continuing the sweep.
