# NEXT work unit (s1120)

HYPOTHESIS-ID: retail-oracle-mode-record-selector-state

Run one phase-gated retail-oracle capture watching the selector/mode state
identified by s1119. The generated audit found `rsViModeType` at `0x8010FF20`
with a boot `osResetType` source, selector bytes `0x8011A862..0x8011A865`
written by render-state unpack/mask paths, and descriptor-index bytes at
`0x8003780C..0x782F`. s1118 proved the RAM table is populated from retail
descriptors and contains non-320 widths.

Before inspecting details, competing hypotheses and discriminator:

- H-retail-selector-stays-320: all watched mode/index/selector state remains
  reset/320-class through the established schedule.
- H-retail-selector-non320: a watched state transition selects a 640/1280
  descriptor before or at the known phase transition.
- H-retail-selector-input-taint: the transition is temporally coupled to a
  verified controller/demo edge rather than reset/lifecycle state.

Discriminator: arm positive whole-RDRAM, PIF, and VI controls in the same
retail run, then compare phase-gated watch hits for `0x10FF20`,
`0x11A862..0x11A865`, and `0x3780C..0x782F` against the verified input edges.
All-zero/320-class state selects H-retail-selector-stays-320; a non-320 index
without input coupling selects H-retail-selector-non320; a transition aligned
with a verified input/demo edge selects H-retail-selector-input-taint. A null
is invalid unless all three positive controls fire.

Commands:

```sh
tools/oracle/build/rs64_oracle \
  --core "$ORACLE_CORE" --rom build/rogue_squadron.z64 --secs 120 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x10FF20:0x10FF21 \
  --watch-write 0x11A862:0x11A866 \
  --watch-write 0x3780C:0x37830 \
  --press 8:start,14:start,20:start,26:start,32:start,38:start,44:start,50:start,56:start \
  --pif-trace --vi-trace
```

Use the repository's configured oracle core path if `$ORACLE_CORE` is unset;
do not accept a zero watch summary without the whole-RDRAM/PIF/VI controls.
Append the phase-qualified classification and ruled-out alternatives to the
ledger and current truth. No port build is needed for this unit.
