# Session 3172 generated-symbol sweep

Command:

```sh
python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x800F0000 --end-address 0x80100000 --limit 16 --require-rename
```

The bounded census selected records that were already synchronized with
companion-qualified names. It reported no generated references to rename and
returned the expected `--require-rename` no-rename error. The printed records
were either `already-synchronized` or explicitly fake/data gaps already using
`data_gap_...` names. The independent generated-definition check over the
interval found no stale `func_...` or `fake_func_...` placeholder definition.

This selects `H-Ambiguous` for the remaining unresolved records and closes
`0x800F0000..0x80100000` for semantic renaming. No source, runtime, build, or
game behavior changed.
