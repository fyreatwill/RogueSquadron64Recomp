# Next: generated-symbol sweep — `func_800E9AE0`

Work unit: perform one bounded generated-symbol audit for the unresolved
mission-overlay placeholder `func_800E9AE0 = 0x800E9AE0`. Do not build or soak.

Competing hypotheses and discriminator:

- H1: the companion decomp map supplies a human semantic name and the generated
  declaration, body, overlay record, callers, and conflicting fragments agree;
  apply the name through the rename mapping.
- H2: a proposed name exists but one or more evidence lines conflict or are
  missing; leave the placeholder unchanged and record the conflict.
- H3: the placeholder is intentionally unresolved, unmaterialized, or already
  synchronized under another name; make no generated-symbol edit.

Discriminating measurement: independently verify the candidate against the
companion symbol files, generated body/declaration, overlay record, callers,
and conflicting fragments. H1 requires all five evidence lines to agree; any
missing or conflicting line selects H2/H3 and forbids a rename.

Suggested bounded commands:
`rg -n '800E9AE0|func_800E9AE0' ../rogue_squadron64 ../N64Recomp/RecompiledFuncs`
and inspect the matching generated body, declaration, overlay record, callers,
and symbol-map fragments.

HYPOTHESIS-ID: generated-symbol-renaming-sweep
