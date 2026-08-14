# NEXT work unit (s1132)

HYPOTHESIS-ID: retail-oracle-active-descriptor-index

Perform one bounded static audit of the remaining active-descriptor boundary:
trace the source of the `0xF0` record pointer passed at `0x8001B720` into
`osViSetMode_recomp`, and classify whether the host VI commit copies width 320
from that record or changes it before commit.

Competing hypotheses and discriminator:

- H-record-pointer-0xF0: the `a0` pointer at `0x8001B720` is the copied table
  base plus `0xF0`, so the committed width comes from the boot-selected record.
- H-pointer-adjusted: control flow or an addend changes `a0` to another copied
  record before the consumer.
- H-consumer-rewrites: `osViSetMode_recomp` or its immediate host path changes
  the width after loading the selected record.

Discriminator: follow `a0` from the selector branch through `0x8001B720`, then
inspect the host `osViSetMode_recomp` implementation for the width load/store.
An unchanged `base+0xF0` pointer and width-320 load selects
H-record-pointer-0xF0; an adjusted pointer selects H-pointer-adjusted; a host
rewrite selects H-consumer-rewrites.

Do not build or run. Use bounded windows only:

```sh
rg -n -C 16 '0x8001B6F0|0x8001B720|osViSetMode_recomp' ../N64Recomp/RecompiledFuncs/funcs_5.c
rg -n -C 12 'osViSetMode_recomp|vi_mode|width' src lib/N64ModernRuntime/ultramodern/src
```
