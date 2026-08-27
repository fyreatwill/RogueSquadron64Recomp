# NEXT work unit (s2841) — generated-symbol-renaming-sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Apply the next bounded source-backed data-gap rename batch to the external
generated snapshot: `0x80041EEC` and `0x800457CC`. Update the regeneration-safe
selector and companion symbol records, then run the bounded selector with
`--require-rename`. Preserve callable-ambiguous records.

## Competing hypotheses and discriminator

- H-source-backed-gap: both records are defined short gaps immediately before
  named routines and can be renamed mechanically to `data_gap_<address>`.
- H-callable: a selected record is callable and must remain a placeholder.
- H-already-synchronized: the generated snapshot has no selected placeholders,
  so the batch is stale and must fail closed.

The discriminator is the selector decision table plus stale-reference scan:
selected entries with nonzero replacements and zero old-name references after
the pass select H-source-backed-gap; any callable/ambiguous classification
selects H-callable for that address; zero replacements selects
H-already-synchronized.

## Exact commands

```sh
python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files \
  --start-address 0x80041000 --end-address 0x80047000 --limit 8 --require-rename
rg -n 'data_gap_80041EEC|data_gap_800457CC|fake_func_80041EEC|fake_func_800457CC' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
```

The selector must report two selected records and a nonzero generated
reference count; the final scan must show only `data_gap_*` names for both
addresses. No game run is required for this symbol-clarity work unit.
