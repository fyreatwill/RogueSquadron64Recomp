# NEXT work unit (s2777) — audit the next generated-symbol interval

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run the regeneration-safe companion census for the next 0x2000-byte interval
after the closed `0x8010F000..0x80111000` region: start at `0x80111000` and
end at `0x80113000`. Preserve data, fake, ambiguous, and already-synchronized
entries. Apply only exact source-backed semantic renames through the existing
rename tooling; do not hand-edit generated C.

## Competing hypotheses and discriminator

- H-placeholder: the interval contains stale generated placeholders with
  defensible companion/source names, and the decision table selects renames.
- H-synchronized: no stale semantic placeholder remains; all candidates are
  synchronized or must be preserved as ambiguous/data.
- H-tooling-gap: a source-backed mismatch exists but the regeneration-safe
  selector/redefs map fails to expose it.

The discriminator is one complete decision table for every candidate in the
interval, plus an independent generated-tree scan for placeholder references.
Selected renames prove H-placeholder; zero selections with no placeholder
references selects H-synchronized; a source-backed candidate missed by the
selector selects H-tooling-gap and requires a tooling fix in this same unit.

## Exact commands

```sh
mkdir -p scratch/agent/s2777_generated_rename
python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs \
  --companion-dir ../rogue_squadron64/symbol_files \
  --start-address 0x80111000 --end-address 0x80113000 --limit 32 \
  --require-rename \
  > scratch/agent/s2777_generated_rename/decision-table.txt 2>&1
rg -n 'func_8011|fake_func_8011|0x8011' \
  ../N64Recomp/RecompiledFuncs/funcs_*.c \
  > scratch/agent/s2777_generated_rename/generated-scan.txt || true
git diff --check
```

If renames are selected, run the existing regeneration-safe map/fixup flow,
build the Debug target, and record the changed files. If the selector returns
the expected zero-selection status, record it as the synchronized outcome and
do not build.
