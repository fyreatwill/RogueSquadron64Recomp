# NEXT work unit — generated-symbol renaming sweep, next bounded placeholder batch

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Classify and synchronize the next unresolved companion placeholder,
`fake_func_800B75C4`, using the companion symbol files and its generated body.
This is a source-only sweep; no build or runtime run is needed. M5 Step 1 is
blocked at VI 640 until a route change supplies title/hangar controls.

Competing hypotheses and the discriminating measurement:

- `H-SemanticMatch`: the companion inventory has an exact callable name at
  `0x800B75C4`; propagate it through the generated snapshot.
- `H-DataGap`: the record is an invalid or non-callable decode with no callable
  prologue and no companion symbol; map it mechanically to
  `data_gap_800B75C4`.
- `H-Ambiguous`: the record has unresolved callable/data or duplicate-symbol
  status; leave it unchanged.

The discriminator is one bounded companion census plus the required-rename
helper. An exact companion result selects `H-SemanticMatch`; a body beginning
with invalid/data-decoded instructions and lacking a callable prologue or
companion symbol selects `H-DataGap`; any conflict selects `H-Ambiguous` and
authorizes no rename.

Exact commands:

```sh
rg -n 'static_.*800B75C4|func_800B75C4|fake_func_800B75C4|0x800B75C4' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_49.c \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
python3 tools/rename_generated_symbols.py \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --start-address 0x800B75C4 --end-address 0x800B75C8 --limit 16 --require-rename
rg -n 'static_.*800B75C4|fake_func_800B75C4|data_gap_800B75C4' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_49.c \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h
```

Expected outcome: add the regeneration-safe mapping only if the census proves
the classification, then synchronize the generated body and header. If the
record is ambiguous,
leave it unchanged and document the conflict; do not build or run the game.
