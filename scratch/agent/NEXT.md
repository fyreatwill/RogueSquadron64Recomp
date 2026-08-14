# NEXT work unit (s1130)

HYPOTHESIS-ID: retail-oracle-active-descriptor-index

Perform one bounded static audit of the next live boundary: identify the
first non-teardown consumer of the boot-selected `0xF0` descriptor after the
resolved `initVideoSubsystem` copy, and determine whether any intervening
generated store can change the active selector or mode record before that
consumer.

Competing hypotheses and discriminator:

- H-no-intervening-store: the copied `0xF0` record reaches the first active
  consumer without an intervening selector/mode-record store.
- H-selector-clobber: a generated store changes selector bytes before that
  consumer.
- H-record-clobber: a generated store changes the copied mode record before
  that consumer.

Discriminator: enumerate all generated stores to selector bytes
`0x8011A862..0x8011A865` and the four copied-record ranges after
`0x8001B66C`, then order them against the first non-teardown consumer call.
An intervening selector or record store selects its corresponding clobber
hypothesis; no intervening store selects H-no-intervening-store.

Do not build or run. Use bounded windows only:

```sh
rg -n 'MEM_[BHW].*(0X8011A862|0X8011A863|0X8011A864|0X8011A865)|0x8011A862|0x8011A863|0x8011A864|0x8011A865' ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -C 12 '0x8001B66C|swapBufferWithViMode|osViSetMode_recomp|buildAndRegisterDefaultMaterial' ../N64Recomp/RecompiledFuncs/funcs_*.c
```
