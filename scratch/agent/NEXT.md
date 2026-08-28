# NEXT work unit (s2961)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Unit

Classify the next unparked generated placeholder after the already-parked
`0x800B42BC` fragment. Re-census the maps first; the next address is expected
to be `0x800B47C4`, subject to current synchronization. This is one bounded
source-table audit. Do not run the game or M5 instrumentation.

## Competing hypotheses and discriminator

- H-Callable: the candidate is a standalone callable function with an exact
  companion semantic name.
- H-Fragment: it is a valid but callable-ambiguous executable fragment; leave
  all names unchanged.
- H-DataGap: it is mechanically bounded non-callable data/fixup; rename it to
  `data_gap_<address>` across every generated and source map.

Discriminate with the complete generated body, exact predecessor/successor
boundaries, all generated callers and independent lookups, return/prologue
evidence, and companion m2c/map names. A callable rename requires an exact
semantic name plus callable evidence. A mechanically proven non-callable
record authorizes a data-gap rename. Otherwise preserve the placeholder.

## Commands

1. Locate the next placeholder after `0x800B42BC` in the project map and
   generated overlay order with `rg`.
2. Read only bounded windows around the candidate in generated C/header,
   project symbols, companion symbols/m2c, and rename tables.
3. Search all generated/source callers and independent lookups.
4. Write the complete table to
   `scratch/agent/s2960_generated_symbol_rename/source-table.md`.
5. If authorized, apply the regeneration-safe rename and build
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RecompiledFuncs`.

Expected outcomes: exact callable mapping or proven data gap produces a
bounded rename and successful build; an ambiguous fragment produces no code
rename but a documented classification. In either case append the result to
`PORTING-STATE.md`, refresh `CURRENT-TRUTH.md`, and commit the iteration.
