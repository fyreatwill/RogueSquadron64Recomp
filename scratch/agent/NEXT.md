# NEXT work unit (s2844) — generated-symbol-renaming-sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Apply the next bounded source-backed data-gap rename batch to the external
generated snapshot in `0x8004A000..0x8004B000`. Update the regeneration-safe
selector and companion symbol record, then run the bounded selector with
`--require-rename`.
Preserve callable-ambiguous records.

## Competing hypotheses and discriminator

- H-source-backed-gap: a record in the interval is a defined short gap
  immediately before a named routine and can be renamed mechanically to
  `data_gap_<address>`.
- H-callable: the selected record is callable and must remain a placeholder.
- H-already-synchronized: the interval has no selected placeholder, so the
  batch is stale and must fail closed.

The discriminator is the selector decision table plus stale-reference scan:
the selected entry with nonzero replacements and zero old-name references after
the pass selects H-source-backed-gap; callable/ambiguous classification
selects H-callable; zero replacements selects H-already-synchronized.

## Exact commands

```sh
python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files \
  --start-address 0x8004A000 --end-address 0x8004B000 --limit 8 --require-rename
rg -n 'data_gap_8004|fake_func_8004' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
```

The selector must report each candidate's classification; a rename selects
H-source-backed-gap only when replacements are nonzero and the old-name scan
is empty. Callable/ambiguous classification selects H-callable; zero
replacements selects H-already-synchronized. The final scan must show no stale
old names for any renamed address. No game run is required.
