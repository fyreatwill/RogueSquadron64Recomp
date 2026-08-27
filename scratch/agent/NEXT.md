# NEXT work unit (s2685) — continue the companion-driven rename batch

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run the companion-driven rename tool against the generated snapshot after
checking the current placeholder census. Apply at most 32 exact semantic
matches from `../rogue_squadron64/symbol_files`; preserve address-named,
`fake_func_`, overlay-collision, or otherwise ambiguous symbols. Review the
tool report and generated diff. Do not infer names from implementation shape.

## Competing hypotheses and discriminator

- `H-exact-batch`: a regenerated snapshot contains companion semantic names
  for current `func_XXXXXXXX` placeholders and can be renamed safely.
- `H-ambiguous`: placeholders remain address-only or collide with existing
  names, so they must be preserved.
- `H-tool-regression`: the bounded tool changes a non-matching symbol or
  exceeds the batch/collision rules.

The discriminator is the exact old-to-new report plus `git diff --check`: a
positive semantic match selects `H-exact-batch`; zero matches with the two
known ambiguous placeholders selects `H-ambiguous`; any out-of-scope edit or
collision selects `H-tool-regression`.

## Ground-truth prerequisite

No runtime watch, build, or soak is authorized for this rename unit.

## Exact commands

1. `python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --limit 32`
2. `python3 -m py_compile tools/rename_generated_symbols.py && git diff --check`
3. Record the report and exact placeholder census in the next ledger entry.
