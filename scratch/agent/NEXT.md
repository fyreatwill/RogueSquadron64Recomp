# NEXT work unit (s2785) — audit the next generated-symbol interval

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run the regeneration-safe companion census for `0x80121000..0x80123000`.
Preserve data, fake, ambiguous, and already-synchronized entries. Apply only
exact source-backed semantic renames through the existing rename tooling.

## Competing hypotheses and discriminator

- H-placeholder: the interval contains stale generated placeholders with
  defensible companion names, so the selector applies renames.
- H-synchronized: the interval has no stale semantic placeholder; candidates
  are synchronized or preserved.
- H-tooling-gap: a source-backed mismatch exists but the selector misses it.

The discriminator is the complete selector decision table plus an independent
numeric-suffix scan of generated definitions. Selected renames prove
H-placeholder; zero selections with no in-range placeholders select
H-synchronized; a source-backed mismatch missed by the selector selects
H-tooling-gap and requires a tooling fix in the same unit.

## Exact commands

```sh
mkdir -p scratch/agent/s2785_generated_rename
python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs \
  --companion-dir ../rogue_squadron64/symbol_files \
  --start-address 0x80121000 --end-address 0x80123000 --limit 32 \
  --require-rename \
  > scratch/agent/s2785_generated_rename/decision-table.txt 2>&1
rg -n 'func_8012|fake_func_8012|0x8012' \
  ../N64Recomp/RecompiledFuncs/funcs_*.c \
  > scratch/agent/s2785_generated_rename/generated-scan.txt || true
perl -ne 'while (/\b(?:func|fake_func)_([0-9A-Fa-f]{8})\b/g) { $v=hex($1); print "$&\n" if $v >= hex("80121000") && $v < hex("80123000") }' \
  ../N64Recomp/RecompiledFuncs/funcs_*.c | sort -u \
  > scratch/agent/s2785_generated_rename/generated-placeholder-in-interval.txt
git diff --check
```

If renames are selected, run the existing regeneration-safe map/fixup flow,
build Debug, and record changed files. If zero selection is returned, record
the synchronized outcome and continue the sweep without inventing names.
