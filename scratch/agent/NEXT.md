# NEXT work unit — generated-symbol renaming sweep, next bounded placeholder batch

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Classify and synchronize the next unclassified generated placeholder,
`static_3_80045024`, using the companion symbol files and its generated body.
This is a source-only sweep; no build or runtime run is needed.

Competing hypotheses and the discriminating measurement:

- `H-SemanticMatch`: the companion inventory has an exact callable name at
  `0x80045024`; propagate it through the generated snapshot.
- `H-DataGap`: the generated record is a non-callable split: it starts with an
  internal label or isolated instruction sequence, has no callable
  prologue or companion symbol, and can be renamed mechanically to
  `data_gap_80045024`.
- `H-Ambiguous`: the record has unresolved callable/data or duplicate-symbol
  status; leave it unchanged.

The discriminator is one bounded census plus the required-rename helper:
the census must show the body/header/overlay references and companion result;
an exact companion result selects `H-SemanticMatch`, while the documented
non-callable shape selects `H-DataGap` and the helper must change every stale
generated reference. Any conflicting or incomplete result selects
`H-Ambiguous` and no rename is authorized.

Exact commands:

```sh
rg -n 'static_3_80045024|func_80045024|fake_func_80045024|0x80045024' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_49.c \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
python3 tools/rename_generated_symbols.py \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --start-address 0x80045024 --end-address 0x80045028 --limit 16 --require-rename
rg -n 'static_3_80045024|data_gap_80045024' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_49.c \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h
```

Expected outcome: add the regeneration-safe mapping only if the census proves
the data-gap classification, then synchronize the generated body and header
with zero stale `static_3_80045024` references.
