# NEXT work unit — generated-symbol renaming sweep, next bounded placeholder batch

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Inventory-select and classify the next unresolved generated placeholder after
`static_4_80106C50`, using its generated body, callers, overlay metadata, and
the companion source tree. This is a source-only sweep; no build or runtime
run is needed. M5 Step 1 is
blocked at VI 640 until a route change supplies title/hangar controls.

Competing hypotheses and the discriminating measurement:

- `H-SemanticMatch`: the companion tree or an independent source/m2c match
  provides an exact semantic name for the selected address; propagate it only with
  corroborating call/body evidence.
- `H-DataGap`: the record is an invalid or non-callable generated split with
  no standalone prologue; map it mechanically to a `data_gap_` name.
- `H-UnresolvedStatic`: it is a standalone callable body, but no defensible
  semantic name exists; leave the generated placeholder unchanged.

The discriminator is one bounded source census plus the required-rename
helper. An exact independent name selects `H-SemanticMatch`; a non-callable
split selects `H-DataGap`; a callable body without a defensible name selects
`H-UnresolvedStatic`.

Exact commands:

```sh
rg -n '^RECOMP_FUNC void (static_|func_|fake_func_)' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -20
rg -n 'static_.*<ADDRESS>|func_<ADDRESS>|fake_func_<ADDRESS>|0x<ADDRESS>' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_49.c \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  /Users/williambuckley/Documents/Tools/rogue_squadron64
python3 tools/rename_generated_symbols.py \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --start-address 0x<ADDRESS> --end-address 0x<END> --limit 16 --require-rename
rg -n 'static_.*<ADDRESS>|fake_func_<ADDRESS>|data_gap_<ADDRESS>' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h
```

Expected outcome: replace `<ADDRESS>`/`<END>` with the inventory-selected
address and add a regeneration-safe mapping only if the census proves the
classification. If the record is callable but ambiguous, leave it unchanged
and document the conflict; do not build or run the game.
