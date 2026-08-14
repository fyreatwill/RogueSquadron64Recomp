# NEXT work unit (s1124)

HYPOTHESIS-ID: retail-oracle-active-descriptor-index

Perform one bounded static audit of the initial lifecycle selector state that
chooses among the NTSC records copied by `initVideoSubsystem`. s1123 resolved
`rsViModeType=0` and found the ROM-backed indices used in call order
`0x7830..0x780C` are `{12,0,6,4,11,9,10,8,13,2}`, with mixed record widths;
the retail width-320 observation therefore requires the active selector to
choose one of `{0,2,4,6}`.

Competing hypotheses and discriminator:

- H-selector-fixed-320: boot selector state chooses one fixed 320-wide record.
- H-selector-runtime-320: lifecycle state chooses a 320-wide record but is
  populated or changed outside the static initializer.
- H-selector-non320: selector state chooses a non-320 record, contradicting
  the independent retail-oracle width-320 observation.

Discriminator: concrete selector values at the initial mode copy and their
writer/data-flow must select one hypothesis. Do not build or run; no
mitigation is authorized.

Exact commands (no build or game run):

```sh
rg -n -C 12 '0x8011A864|0x8011A865|0x8011A862|selectAndApplyViMode|swapBufferWithViMode' ../N64Recomp/RecompiledFuncs/funcs_5.c ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -C 8 '8011A864|8011A865|8011A862' /Users/williambuckley/Documents/Tools/rogue_squadron64/docs/mips_to_c /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Use bounded `sed` windows around each selector writer and the initial mode
copy. Append the fixed/runtime/non-320 classification to the ledger and
current truth. No mitigation is authorized.
