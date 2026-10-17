# Next: generated-symbol sweep — `load_level_hmp`

Work unit: perform one bounded generated-symbol rename candidate for
`load_level_hmp = 0x80043D74`. Do not build or soak.

Competing hypotheses and discriminator:

- H1: the companion decomp map, generated declaration, body, overlay record,
  and callers agree on `load_level_hmp`; apply the human name.
- H2: only some evidence agrees or conflicting fragments exist; leave the
  placeholder unchanged and record the conflict.
- H3: the candidate is already synchronized, absent, or unmaterialized; make
  no generated-symbol edit and select the next ranked candidate later.

Discriminating measurement: independently verify the candidate against the
body, declaration, overlay record, callers, and conflicting fragments. H1
requires all five evidence lines to agree; any missing or conflicting line
selects H2/H3 and forbids a rename.

Suggested bounded commands:
`rg -n '80043C30|markHighLodCellsInGrid|func_80043C30' . --glob '!PORTING-STATE.md'`
then inspect the matched generated function, companion decomp symbol/map, and
the existing rename audit before changing the fixup mapping. If synchronized,
record that fact instead of editing.

Session 5322 result: `markHighLodCellsInGrid` was H3/already synchronized;
all five evidence lines agreed and no generated edit was made.

HYPOTHESIS-ID: generated-symbol-renaming-sweep
