# NEXT work unit — generated-symbol renaming sweep, next bounded placeholder batch

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

Classify and synchronize the next unclassified generated placeholder,
`static_3_800A2114`, using the companion symbol files and its generated body.
This is a source-only sweep; no build or runtime run is needed.

Competing hypotheses and the discriminating measurement:

- `H-SemanticMatch`: the companion inventory has an exact callable name at
  `0x800A2114`; propagate it through the generated snapshot.
- `H-DataGap`: the record is an invalid or non-callable decode with no
  callable prologue and no companion symbol; map it mechanically to
  `data_gap_800A2114`.
- `H-Ambiguous`: the record has unresolved callable/data or duplicate-symbol
  status; leave it unchanged.

The discriminator is one bounded census plus the required-rename helper. An
exact companion result selects `H-SemanticMatch`; a body beginning with
invalid/data-decoded instructions and lacking a callable prologue or
companion symbol selects `H-DataGap`, after adding the regeneration-safe
mapping if needed. Any conflict selects `H-Ambiguous` and authorizes no
rename.

Exact commands:

```sh
rg -n 'static_3_800A2114|func_800A2114|fake_func_800A2114|0x800A2114' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_49.c \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
python3 tools/rename_generated_symbols.py \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --start-address 0x800A2114 --end-address 0x800A2118 --limit 16 --require-rename
rg -n 'static_3_800A2114|data_gap_800A2114' \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_49.c \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h
```

Expected outcome: add the regeneration-safe mapping only if the census proves
the data-gap classification, then synchronize the generated body and header
with zero stale `static_3_800A2114` references.
