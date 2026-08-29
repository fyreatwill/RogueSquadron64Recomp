# NEXT work unit — generated-symbol renaming sweep, next bounded placeholder batch

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Single work unit

M5 remains blocked pending a route change. The selected M3 class
`musyxMixActiveVoices` was proven range-safe in Session 3167. Sessions 3168
through 3179 closed the latest bands without a stale semantic placeholder.
Session 3180 synchronized two concrete data-gap records outside the latest
high-address bands. Session 3181 closed `0x80170000..0x80180000` with no
generated placeholder body or rename candidate. Resume the regeneration-safe
sweep at `0x80180000..0x80190000`.

Competing hypotheses and the discriminating measurement:

- `H-SemanticMatch`: a placeholder has an exact companion-qualified semantic
  function name and can be propagated without ambiguity.
- `H-DataGap`: a placeholder is independently classified as a non-callable
  fragment and can be renamed mechanically to `data_gap_<address>`.
- `H-Ambiguous`: the companion record is fake/duplicate/overlay-colliding or
  lacks enough evidence; it must remain unchanged.

The discriminator is one bounded sweep table: every candidate in the selected
interval is classified against companion symbols and generated definitions,
then the helper must report at least one changed reference. An exact match
selects SemanticMatch or DataGap; ambiguous entries remain untouched.

Exact starting commands:

```sh
python3 tools/rename_generated_symbols.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files --start-address 0x80180000 --end-address 0x80190000 --limit 16 --require-rename
rg -n '^RECOMP_FUNC void (func|fake_func|static)_[^(]+\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | rg '8018[0-9A-Fa-f]{4}|8019[0-9A-Fa-f]{4}' || true
```

Expected outcome: the next batch either renames at least one exact candidate,
or proves the bounded interval contains only synchronized/ambiguous entries;
if the latter occurs, select the next address band in the same sweep.
