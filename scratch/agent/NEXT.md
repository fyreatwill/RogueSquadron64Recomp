# NEXT work unit (s2865) — generated-symbol-renaming-sweep

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run the next bounded source-backed symbol sweep over `0x80073500..0x80074500`.
Apply only exact companion semantic renames or mechanically proven data-gap
renames; preserve callable-ambiguous records.

## Competing hypotheses and discriminator

- H-source-backed-gap: the interval contains a defined short non-callable
  record that can be renamed to `data_gap_<address>`.
- H-callable: a placeholder is callable or semantically unresolved and must
  remain unchanged.
- H-already-synchronized: no selected placeholder remains in the interval.

The discriminator is the selector decision table plus the final bounded
stale-name scan. Nonzero replacements with no old-name hits selects
H-source-backed-gap; ambiguous/callable preservation selects H-callable; zero
replacements selects H-already-synchronized.

## Exact commands

```sh
python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files \
  --start-address 0x80073500 --end-address 0x80074500 --limit 8
rg -n 'data_gap_8007|fake_func_8007' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
```

No build or game run is required for this source-backed rename unit.
