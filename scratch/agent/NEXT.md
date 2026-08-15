# NEXT work unit (s1235)

HYPOTHESIS-ID: retail-reset-context-consumers

Run one bounded static generated/companion census of every use of the
retail-only PIF/IPL3 boot context: `s3..s7` (`r19..r23`), `t3` (`r11`), boot
`sp` (`r29`), and boot `ra` (`r31`). Compare those uses with the port's
`recomp_context` initialization and the first overwrites on the generated game
path. Do not build or run.

Competing hypotheses and discriminator:

- H1: at least one skipped PIF/IPL3 register is consumed before it is
  overwritten, so the port's direct entry can explain the divergence.
- H2: all skipped registers are dead or overwritten before use; the mismatch
  is real but cannot explain the stable VI-320 path.
- H3: only stack/return bookkeeping differs, while all game-visible boot
  context is overwritten before use; this is a narrower H2 outcome.

Discriminator: a complete register-use table with first read, first write,
and consumer function for each of `r11`, `r19..r23`, `r29`, and `r31` from
`recomp_entrypoint` through idle/video bootstrap. A pre-overwrite read selects
H1; no such read selects H2; only `r29/r31` bookkeeping use selects H3.

Exact commands:

```
rg -n 'ctx->r(11|19|20|21|22|23|29|31)|r(11|19|20|21|22|23|29|31)' ../N64Recomp/RecompiledFuncs/funcs_0.c ../N64Recomp/RecompiledFuncs/funcs.h
rg -n -C 5 's3|s4|s5|s6|s7|t3|A4001FF0|A4001550|reset_type|r4300_gpregs\[(19|20|21|22|23|11|29|31)\]' /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/device/pif /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/device/r4300
rg -n -C 5 'recomp_entrypoint|run_thread_function|thread_create_callback|ctx\.r(11|19|20|21|22|23|29|31)' lib/N64ModernRuntime/librecomp/src src/main
```

Record the first read/write and consumer for every listed register, then state
which hypothesis the complete table selects.
