# NEXT work unit — generated-symbol renaming sweep, next bounded placeholder batch

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Classify the next unresolved generated placeholder,
`static_4_80106C50`, using its generated body, callers, overlay metadata, and
the companion source tree. This is a source-only sweep; no build or runtime
run is needed. M5 Step 1 is
blocked at VI 640 until a route change supplies title/hangar controls.

Competing hypotheses and the discriminating measurement:

- `H-SemanticMatch`: the companion tree or an independent source/m2c match
  provides an exact semantic name for `0x80106C50`; propagate it only with
  corroborating call/body evidence.
- `H-DataGap`: the record is an invalid or non-callable generated split with
  no standalone prologue; map it mechanically to `data_gap_80106C50`.
- `H-UnresolvedStatic`: it is a standalone callable body, but no defensible
  semantic name exists; leave the static placeholder unchanged.

The discriminator is one bounded source census plus the required-rename
helper. An exact independent name selects `H-SemanticMatch`; a non-callable
split selects `H-DataGap`; a callable body without a defensible name selects
`H-UnresolvedStatic`.

Exact commands:

```sh
rg -n 'static_.*80106C50|func_80106C50|fake_func_80106C50|0x80106C50|0x8010A948' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_49.c \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  /Users/williambuckley/Documents/Tools/rogue_squadron64
python3 tools/rename_generated_symbols.py \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --start-address 0x80106C50 --end-address 0x80106C54 --limit 16 --require-rename
rg -n 'static_.*80106C50|fake_func_80106C50|data_gap_80106C50' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_49.c \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h
```

Expected outcome: add the regeneration-safe mapping only if the census proves
the classification, then synchronize the generated body and header. If the
record is ambiguous,
leave it unchanged and document the conflict; do not build or run the game.
