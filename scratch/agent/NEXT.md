# NEXT work unit (s1128)

HYPOTHESIS-ID: retail-oracle-active-descriptor-index

Perform one bounded static audit of the conditional descriptor writes in
`initVideoSubsystem` after the initial mode-table loads. Determine whether the
boot path preserves the index-0 descriptor in stack block `sp+0x108` before
the four records are copied at `0x8001B66C`, or overwrites it with another
NTSC index.

Competing hypotheses and discriminator:

- H-preserve-index0: boot control flow does not take a later write to
  `sp+0x108`, so destination offset `0xF0` remains NTSC index 0 / width 320.
- H-replace-index: a boot-reachable conditional writes `sp+0x108` after the
  initial `0x782C` load; the replacement index and width differ.
- H-copy-source-misread: the `0xF0` destination is not sourced from
  `sp+0x108`, despite the four-record copy loop's arithmetic.

Discriminator: enumerate every store-producing block for `sp+0x108` and its
branch predicate, then evaluate the boot arguments from `initVideoBootWrapper`.
No later store proves H-preserve-index0; a boot-taken later store proves
H-replace-index; any alternate source arithmetic proves H-copy-source-misread.

Do not build or run. Use bounded windows only:

```sh
rg -n -C 18 'addiu       \$a3, \$sp, 0x108|sw[[:space:]]+\$v[0-9], 0x108\(\$sp\)|0x8001A3D0|0x8001AD90|0x8001B25C|0x8001B2F8|0x8001B66C|0x8001B680' ../N64Recomp/RecompiledFuncs/funcs_5.c
sed -n '29690,29735p' ../N64Recomp/RecompiledFuncs/funcs_4.c
sed -n '4045,4185p' ../N64Recomp/RecompiledFuncs/funcs_5.c
```
