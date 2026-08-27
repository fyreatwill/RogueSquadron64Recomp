# NEXT work unit (s2767) — synchronize the next generated-symbol interval

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Synchronize the bounded generated-function interval `0x80105000..0x80107000`
using companion decomp names and the regeneration-safe rename map. Preserve
ambiguous, fake, and address-only placeholders; do not invent semantic names.

## Result of s2766

The interval contained no stale semantic placeholder. The four generated
placeholders were `fake_func_8010357C`, `fake_func_80103D08`,
`fake_func_80104208`, and `fake_func_801044D8`; all remain preserved as
ambiguous/fake. The rename tool returned its expected no-rename status, and an
independent scan found no other placeholder in the interval.

## Competing hypotheses and discriminator for s2767

- H1: every stale placeholder in the interval has a defensible companion/source name.
- H2: some placeholders are fake/address-only or ambiguous and must remain.
- H3: an apparent match is a duplicate/alias whose references make renaming unsafe.

The discriminator is the complete interval census: classify every companion
candidate as source-backed rename, already synchronized, preserved
ambiguous/fake/address-only, or unsafe alias, then independently scan the
generated tree for unresolved placeholders.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. `rg -n 'func_(80105|80106)|fake_func_(80105|80106)' ../N64Recomp/RecompiledFuncs/`
3. `mkdir -p scratch/agent/s2767_generated_rename`
4. `python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address 0x80105000 --end-address 0x80107000 --limit 32 --require-rename > scratch/agent/s2767_generated_rename/census.txt 2>&1`
5. Verify with `git diff --check` and an independent interval placeholder scan; save all census artifacts under `scratch/agent/s2767_generated_rename/`.

Expected outcomes: a nonzero rename count advances the synchronized region;
zero stale placeholders closes this interval as already synchronized; fake or
conflicting entries are preserved and logged with their classification. Do not
build when the census changes no generated code. Preserve ambiguous, fake, and
address-only entries.
