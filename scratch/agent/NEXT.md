# NEXT work unit (s2764) — synchronize the next generated-symbol interval

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Synchronize the bounded generated-function interval `0x800FF000..0x80101000`
using companion decomp names and the regeneration-safe rename map. Preserve
ambiguous, fake, and address-only placeholders; do not invent semantic names.

## Competing hypotheses and discriminator

- H1: every stale placeholder in the interval has a defensible companion/source name.
- H2: some placeholders are fake/address-only or ambiguous and must remain.
- H3: an apparent match is a duplicate/alias whose references make renaming unsafe.

The discriminator is the complete interval census: classify every companion
candidate as source-backed rename, already synchronized, preserved
ambiguous/fake/address-only, or unsafe alias, then independently scan the
generated tree for unresolved placeholders.

## Exact commands

1. `grep -n '^## Session ' PORTING-STATE.md | tail -15`
2. `rg -n 'func_(800FF|80100)|fake_func_(800FF|80100)' ../N64Recomp/RecompiledFuncs/`
3. `python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address 0x800FF000 --end-address 0x80101000 --limit 32 --require-rename`
4. Verify with `git diff --check` and an independent interval placeholder scan; save the census under `scratch/agent/s2764_generated_rename/`.

Expected outcomes: a nonzero rename count advances the synchronized region;
zero stale placeholders closes this interval as already synchronized; fake or
conflicting entries are preserved and logged with their classification. The
previous widened interval renamed only the two known invalid data gaps as
`data_gap_*`; no function body or runtime behavior changed.
