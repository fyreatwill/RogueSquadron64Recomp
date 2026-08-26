# NEXT work unit (s2451) — audit whether rs_memset consumes guest ra

HYPOTHESIS-ID: m5-port-static-rsmemset-callsite

## Work unit

Perform a bounded static audit of the complete generated `rs_memset` body and
the retail MIPS body around `0x800078E0`, specifically every read or write of
`$ra` and every return-dependent branch. Do not change runtime or generated
output.

## Competing hypotheses and discriminator

- H-RsMemsetDoesNotConsumeRA: zero `ctx->r31` cannot explain the missing
  second-range consumer.
- H-RsMemsetConsumesRA: the callee's control flow or data accesses depend on
  the guest link and the no-link call contract is semantically relevant.
- H-RetailPortBodyDiffers: the retail body has a return/link dependency absent
  from the generated body or the port's observed path.

The discriminator is a complete `$ra` use table: zero `$ra` reads and no
return-dependent branch in both bodies selects H-RsMemsetDoesNotConsumeRA; a
live `$ra` use in both selects H-RsMemsetConsumesRA; a retail-only use selects
H-RetailPortBodyDiffers. Any incomplete body or missing retail disassembly is
non-discriminating and must not be promoted.

## Exact commands

`sed -n '6800,6895p' ../N64Recomp/RecompiledFuncs/funcs_2.c`

`rg -n -C 3 "800078E0|800078EC|80007900|\$ra|r31" ../N64Recomp/RecompiledFuncs/funcs_2.c`

`rg -n -C 3 "800078E0|800078EC|80007900|ra|jr" tools/oracle scratch docs | head -240`
