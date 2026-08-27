# NEXT work unit (s2834) — continue generated-symbol renaming sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Apply the persistent bounded rename batch for three short main-overlay
records: `fake_func_8001C3FC`, `fake_func_80023968`, and
`fake_func_80024128` → `data_gap_*`. These records immediately precede named
functions in the companion map, so the selected names make their
non-callable status explicit. Do not run the game or regenerate the external
tree in this unit.

## Competing hypotheses and discriminator

- H-companion-gap: each selected fake record is a non-callable fragment and
  can safely use an explicit `data_gap_*` name.
- H-real-function: at least one selected record is a callable function whose
  placeholder must be retained until a semantic name is established.
- H-stale-snapshot: the external generated snapshot no longer contains one
  or more selected placeholders, so the batch is already synchronized there.

The discriminator is one bounded selector run plus an independent generated
tree scan: the selector must report exactly the three selected mappings and
nonzero replacements, and the scan must find all three `data_gap_*` names with
no corresponding `fake_func_*` references. Any missing replacement selects
H-stale-snapshot for that entry; a callable body or non-adjacent companion
layout rejects H-companion-gap and stops further renaming of that entry.

## Exact commands

```sh
python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs \
  --start-address 0x8001C3FC --end-address 0x80024130 --limit 32 \
  --require-rename
rg -n -E 'data_gap_8001C3FC|data_gap_80023968|data_gap_80024128|fake_func_8001C3FC|fake_func_80023968|fake_func_80024128' \
  ../N64Recomp/RecompiledFuncs
git diff --check
```

No build or soak is needed: this is a regeneration-safe symbol-clarity
batch, and the generated snapshot is external to this checkout.
