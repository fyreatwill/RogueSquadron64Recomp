# NEXT work unit (s1125)

HYPOTHESIS-ID: retail-oracle-active-descriptor-index

Perform one bounded static audit of the boot caller's `$s1` render-state
argument passed to `buildAndRegisterDefaultMaterial` at `0x80017B88`.
The prior audit established that selector bytes `0x8011A865/64/62` are derived
from bits 8/7, 5/4/3, and 2 of `$s1`, and that the retail width-320 path must
choose copied-record offsets `0x00/0x50/0xA0` (indices `{0,2,4,6}`).

Competing hypotheses and discriminator:

- H-boot-arg-fixed: the boot caller supplies a statically fixed render-state
  value selecting one concrete 320 record.
- H-boot-arg-runtime: the boot argument is assembled from runtime display/config
  state, so the concrete selector cannot be resolved statically at the caller.
- H-boot-arg-non320: the boot argument selects a non-320 record, contradicting
  the independent retail-oracle width-320 observation.

Discriminator: trace the argument loads/stores immediately before the boot call
to `buildAndRegisterDefaultMaterial` and decode bits 2, 3, 4, 5, 7, and 8.
A concrete value selecting `{0,2,4,6}` proves H-boot-arg-fixed; a runtime
load/merge proves H-boot-arg-runtime; a concrete non-320 choice would require
reconciling or overturning the retail observation. Do not build or run.

Exact commands:

```sh
rg -n -C 30 '0x800183F8|0x800185DC|buildAndRegisterDefaultMaterial\(' ../N64Recomp/RecompiledFuncs/funcs_4.c
rg -n -C 20 'initVideoBootWrapper|advanceVideoFrame|0x800183[BCDE]|0x800185[D-F]' ../N64Recomp/RecompiledFuncs/funcs_4.c
rg -n -C 8 'buildAndRegisterDefaultMaterial|initVideoBootWrapper|advanceVideoFrame' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/main_overlay.txt /Users/williambuckley/Documents/Tools/rogue_squadron64/docs/mips_to_c
```

Use bounded `sed` windows around both call sites. Append the argument/value
classification to the ledger and current truth. No mitigation is authorized.
