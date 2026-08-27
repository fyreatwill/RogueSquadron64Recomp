# NEXT work unit (s2842) — generated-symbol-renaming-sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Apply the next bounded source-backed data-gap rename batch to the external
generated snapshot: `0x800496F4`. Update the regeneration-safe selector and
companion symbol record, then run the bounded selector with `--require-rename`.
Preserve callable-ambiguous records.

## Competing hypotheses and discriminator

- H-source-backed-gap: the record is a defined short gap immediately before a
  named routine and can be renamed mechanically to `data_gap_<address>`.
- H-callable: the selected record is callable and must remain a placeholder.
- H-already-synchronized: the generated snapshot has no selected placeholder,
  so the batch is stale and must fail closed.

The discriminator is the selector decision table plus stale-reference scan:
the selected entry with nonzero replacements and zero old-name references after
the pass selects H-source-backed-gap; callable/ambiguous classification
selects H-callable; zero replacements selects H-already-synchronized.

## Exact commands

```sh
python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files \
  --start-address 0x80049000 --end-address 0x8004A000 --limit 8 --require-rename
rg -n 'data_gap_800496F4|fake_func_800496F4' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
```

The selector must report one selected record and a nonzero generated
reference count; the final scan must show only `data_gap_800496F4`. No game run
is required for this symbol-clarity work unit.
