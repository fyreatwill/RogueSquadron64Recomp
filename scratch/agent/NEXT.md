# NEXT work unit (s2772) — bounded generated-symbol rename interval

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Work unit

Run the regeneration-safe companion census for `0x8010D000..0x8010F000`,
then apply only exact semantic companion mappings to the checked-in symbol
map and generated tree. Preserve ambiguous, fake, data, and address-only
entries. This is a bounded rename batch; do not run the stalled M5
re-baseline in this iteration.

## Competing hypotheses and discriminator

- H-Semantic: a companion semantic name is present for a generated
  placeholder; address, old placeholder, and new name must all match before
  rename.
- H-Ambiguous: the address is a fake/data/address-only fragment or has
  conflicting companion names; it must remain unchanged.
- H-Synchronized: the generated tree already carries the companion name; the
  symbol map may only be reconciled if its checked-in name is stale.

The discriminating measurement is the complete address-keyed decision table:
every companion candidate in the interval classified as selected,
already-synchronized, ambiguous-or-fake, or conflicting, plus generated
reference counts before and after. A selected row must produce a nonzero
rename and no duplicate destination; zero selected rows closes the interval,
and does not authorize inventing a name.

## Exact commands

1. `python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address 0x8010D000 --end-address 0x8010F000 --limit 32 --require-rename`
2. Inspect bounded decision output and run `git diff --check`.

Expected outcomes: semantic candidates either rename exactly or are shown
already synchronized; ambiguous/fake entries remain unchanged. If a mapping
lands, regenerate only through the documented pipeline before claiming the
generated output is updated.
