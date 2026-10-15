# s4888 generated-symbol rename audit

The available generated tree contains only two placeholder function identifiers: `func_8000040C` and `func_800E9AE0`.

- `func_8000040C` has one live caller (`main`), but no semantic companion mapping exists at `0x8000040C`; no exact semantic span can be established.
- `func_800E9AE0` has no generated caller. The companion `mission_overlay.txt` deliberately preserves it, documents that a false `func_800E9B10` reference splits this real function, and marks nearby entries as data gaps/intentional fake boundaries.

The state-machine census found zero jump-table and zero repeated-state-write candidates. The prescribed `rename_generated_symbols.py` tool is absent; `generated_symbol_batch.py` has an unrelated fixed mapping. No generated or companion file was changed.
