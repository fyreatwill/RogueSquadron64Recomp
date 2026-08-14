# NEXT work unit (s1118)

HYPOTHESIS-ID: retail-oracle-mode-record-population

Perform one bounded static audit of the producer/copy path that populates the
mode records at `0x80128D50`, including selector-byte producers and the
static descriptor source. Do not build or run another oracle capture; s1116
controls were positive and s1117 ruled out pointer escape but left table
population and concrete widths open.

Before inspecting details, competing hypotheses and discriminator:

- H-mode-record-constant: the producer copies fixed 320-width descriptors.
- H-mode-record-state-gate: selector state chooses descriptors whose widths
  differ across lifecycle phases.
- H-mode-record-uninitialized: the table has no valid producer before the
  first `osViSetMode`, so the observed width is stale/zero-initialized data.

Discriminator: identify every writer/copy into `0x80128D50..0x80128E3F`, the
descriptor source/index, and each record's `+8` width. Fixed 320 descriptors
select H-mode-record-constant; state-dependent descriptor selection with a
non-320 record selects H-mode-record-state-gate; no producer before the first
mode application selects H-mode-record-uninitialized. If unresolved, record
the exact missing writer boundary and choose one source-level witness; do not
add another runtime field.

Commands:

```sh
rg -n "80128D50|D_80128D50|-0x72B0|0x80039330|8000273C|osViSetMode" ../N64Recomp/RecompiledFuncs ../rogue_squadron64 syms docs
rg -n "8011A864|8011A865|8011A862|80017CA0|80017CB0|80017CD0|80017CEC" ../N64Recomp/RecompiledFuncs ../rogue_squadron64 syms docs
```

Read only bounded windows around hits; append the classification and ruled-out
alternatives to `PORTING-STATE.md` and `docs/CURRENT-TRUTH.md`.
