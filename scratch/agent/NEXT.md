# NEXT work unit (s1119)

HYPOTHESIS-ID: retail-oracle-mode-record-selector-state

Perform one bounded static audit of the producer path for selector bytes
`0x8011A864`, `0x8011A865`, and `0x8011A862`, plus the `getViModeType` value
that indexes the descriptor arrays at `0x8003780C..0x782F`. Do not build or
run another oracle capture; s1118 proved the RAM table is populated from
retail descriptors and contains non-320 widths.

Before inspecting details, competing hypotheses and discriminator:

- H-selector-fixed-zero: the mode-type/index state remains zero or selects
  only the 320 descriptor class on the established retail path.
- H-selector-lifecycle: a lifecycle/config predicate changes the mode-type or
  selector bytes and can select a 640/1280 descriptor before the phase gate.
- H-selector-input-or-demo: controller/demo state directly or indirectly
  drives the selector/index transition.

Discriminator: enumerate every generated/companion writer and every caller of
the mode-type/index producer, then classify the controlling input. A complete
zero/320-only path selects H-selector-fixed-zero; a lifecycle/config branch
with a non-320 index selects H-selector-lifecycle; a controller/demo-tainted
branch selects H-selector-input-or-demo. If unresolved, record the exact
missing writer boundary and choose one source-level witness; do not add a
runtime field.

Commands:

```sh
rg -n "80128D50|D_80128D50|-0x72B0|0x80039330|8000273C|osViSetMode" ../N64Recomp/RecompiledFuncs ../rogue_squadron64 syms docs
rg -n "8011A864|8011A865|8011A862|80017CA0|80017CB0|80017CD0|80017CEC|8000273C|8003780C|8003782F" ../N64Recomp/RecompiledFuncs ../rogue_squadron64 syms docs
```

Read only bounded windows around hits; append the classification and ruled-out
alternatives to `PORTING-STATE.md` and `docs/CURRENT-TRUTH.md`. Do not run a
build or runtime capture for this unit.
