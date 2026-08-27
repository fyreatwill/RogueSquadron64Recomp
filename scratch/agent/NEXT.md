# NEXT work unit (s2761) — synchronize the next generated-symbol interval

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Synchronize the bounded generated-function interval `0x800F7000..0x800F9000`
using companion decomp names and the regeneration-safe rename map. Preserve
ambiguous, fake, and address-only placeholders; do not invent semantic names.

## Competing hypotheses and discriminator

- H1: every stale placeholder in the interval has a defensible companion/source name.
- H2: some placeholders are fake/address-only or ambiguous and must remain.
- H3: an apparent match is a duplicate/alias whose references make renaming unsafe.

The discriminator is the complete interval census: classify every companion
candidate as source-backed rename, already synchronized, preserved
ambiguous/fake/address-only, or unsafe alias, then verify the generated tree
has no unresolved stale placeholders in the interval.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. `rg -n 'func_(800F7|800F8)|fake_func_(800F7|800F8)' ../N64Recomp/RecompiledFuncs/`
3. Run the bounded rename census/map tooling for `0x800F7000..0x800F9000`,
   then apply only source-backed matches.
4. Verify with `git diff --check` and the rename-tool reference/count check;
   save the census under `scratch/agent/s2761_generated_rename/`.

Expected outcomes: a nonzero rename count advances the synchronized region;
zero stale placeholders closes this interval as already synchronized; fake or
conflicting entries are preserved and logged with their classification.
