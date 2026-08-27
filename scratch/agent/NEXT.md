# NEXT work unit (s2759) — synchronize the next generated-symbol interval

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Synchronize the bounded generated-function interval `0x800F3000..0x800F5000`
using companion decomp names and the regeneration-safe rename map. Preserve
ambiguous, fake, and address-only placeholders; do not invent semantic names.

## Competing hypotheses and discriminator

- H1: every placeholder in the interval has a defensible companion/source name.
- H2: some placeholders are fake/address-only or ambiguous and must remain.
- H3: an apparent match is a duplicate/alias whose references make renaming
  unsafe.

The discriminator is the interval census: classify every address as a
source-backed rename, preserved ambiguous/fake/address-only, or unsafe alias;
selected edits must have matching generated references and no unresolved old
names in the interval.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. `rg -n 'func_(800F3|800F4)' ../N64Recomp/RecompiledFuncs/`
3. Run the existing bounded rename census/map tooling for
   `0x800F3000..0x800F5000`, then apply only source-backed matches.
4. Verify with `git diff --check` and the rename-tool reference/count check;
   save the census under `scratch/agent/s2759_generated_rename/`.
