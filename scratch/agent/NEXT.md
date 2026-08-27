# NEXT work unit (s2760) — synchronize the next generated-symbol interval

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Synchronize the bounded generated-function interval `0x800F5000..0x800F7000`
using companion decomp names and the regeneration-safe rename map. Preserve
ambiguous, fake, and address-only placeholders; do not invent semantic names.

## Competing hypotheses and discriminator

- H1: every stale placeholder in the interval has a defensible companion/source name.
- H2: some placeholders are fake/address-only or ambiguous and must remain.
- H3: an apparent match is a duplicate/alias whose references make renaming unsafe.

The discriminator is the interval census: classify every address as a
source-backed rename, already synchronized, preserved ambiguous/fake/address-
only, or unsafe alias; selected edits must have matching generated references
and no unresolved old names in the interval.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. `rg -n 'func_(800F5|800F6)|fake_func_(800F5|800F6)' ../N64Recomp/RecompiledFuncs/`
3. Run the existing bounded rename census/map tooling for
   `0x800F5000..0x800F7000`, then apply only source-backed matches.
4. Verify with `git diff --check` and the rename-tool reference/count check; save
   the census under `scratch/agent/s2760_generated_rename/`.

Expected outcomes: a nonzero rename count advances the synchronized region;
zero stale placeholders closes this interval as already synchronized; fake or
conflicting entries are preserved and logged with their classification.
