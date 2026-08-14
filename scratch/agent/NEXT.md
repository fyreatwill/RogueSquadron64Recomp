# NEXT work unit (s1121)

HYPOTHESIS-ID: retail-oracle-mode-record-selector-state

Perform one bounded static audit of the retail `osResetType`/mode-table input
boundary and the concrete producer of descriptor-index bytes
`0x8003780C..0x8003782F`. s1120 passed the independent oracle controls and
found zero writes to `rsViModeType` and the descriptor-index range, with only
four pre-input writes somewhere in selector range `0x8011A862..0x8011A865`.
The oracle hit-print cap hid their individual addresses and values; do not
turn that capture into a concrete selector-value claim.

Competing hypotheses and discriminator:

- H-reset-derived-index: `osResetType`/`rsViModeType` selects the active
  descriptor-index record through a generated lifecycle path.
- H-fixed-index-caller: the active record index is supplied by a fixed or
  constant caller path, independent of reset mode.
- H-non-generated-index-source: the generated census misses the active index
  producer at a raw, host, overlay, or data-driven boundary.

Discriminator: enumerate every generated read/write and caller of
`rsViModeType`, `getViModeType`, `0x8003780C..0x782F`, and the mode-table copy
routine; reconcile each with companion references, overlay/data symbols, and
the retail ROM bytes. A reset-dominated index path selects H-reset-derived-index;
a constant/fixed caller selects H-fixed-index-caller; no complete generated or
companion owner selects H-non-generated-index-source. The audit must record the
exact address/field and caller predicate for whichever arm wins.

Exact commands (no build or game run):

```sh
rg -n 'rsViModeType|getViModeType|setViModeType|8003780C|8003780c|3780C|3780c|osResetType|osViModeTable|initVideoSubsystem|selectAndApplyViMode|swapBufferWithViMode' RecompiledFuncs rogue_squadron64 syms docs
rg -n '0x8010FF20|0x8003780C|0x8003780c|0x8011A862|0x8011A864|0x80128D50|0x80039330' src lib patches syms RecompiledFuncs rogue_squadron64
rg -n 'rsViModeType|getViModeType|setViModeType|osResetType|osViModeTable|3780' rogue_squadron64 -g '*.[ch]' -g '*.toml'
```

Use bounded `sed` windows around every hit; do not read `PORTING-STATE.md`.
Append the classified boundary and ruled-out alternatives to the ledger and
current truth. No mitigation is authorized.
