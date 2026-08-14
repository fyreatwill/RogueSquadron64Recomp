# NEXT work unit (s1129)

HYPOTHESIS-ID: retail-oracle-active-descriptor-index

Perform one bounded static audit of the recurring material-writer path after
the boot descriptor chain is fixed. Determine whether the recurring
`buildAndRegisterDefaultMaterial` call can change selector bytes before the
first active VI mode selection, or only after the boot `0xF0` record has been
copied.

Competing hypotheses and discriminator:

- H-boot-first: the boot call copies the `0xF0` index-0 record before any
  recurring material writer can alter selector state.
- H-recurring-first: a recurring material-writer call is boot-reachable before
  the first `selectAndApplyViMode`/copy consumer and changes the selector.
- H-selector-independent: the recurring writer may run early, but its writes
  cannot affect the first mode selection because the consumer uses a separate
  state or ordering barrier.

Discriminator: enumerate every generated caller of
`buildAndRegisterDefaultMaterial` and the first generated caller/consumer order
for `selectAndApplyViMode` or the `0x8001B66C` copy. A caller before the first
consumer with a selector-changing argument proves H-recurring-first; all
writer calls after the first consumer prove H-boot-first; an early writer plus
independent selector state/order proves H-selector-independent.

Do not build or run. Use bounded windows only:

```sh
rg -n -C 18 'buildAndRegisterDefaultMaterial|selectAndApplyViMode|0x8001B66C|0x80017B88|0x8001C' ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -C 12 'buildAndRegisterDefaultMaterial|selectAndApplyViMode' rogue_squadron64/src rogue_squadron64/include
```
