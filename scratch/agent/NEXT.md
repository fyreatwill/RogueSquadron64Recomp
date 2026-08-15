# NEXT work unit (s1236)

HYPOTHESIS-ID: retail-reset-context-cp0

Run one bounded static generated/retail census of the non-GPR reset context:
CP0 status/config, PIF reset type, and any OS reset-context memory populated by
PIF/IPL3. Compare each field's first generated read and first write with the
port runtime's initialization and `getOsResetType` path. Do not build or run.

Competing hypotheses and discriminator:

- H1: a CP0/reset-context value is consumed by generated code before overwrite;
  the direct port entry can explain the stable VI-320 divergence.
- H2: every such value is dead or overwritten before game-visible use; the
  remaining mismatch is outside this reset-context class.
- H3: only host/runtime bookkeeping observes the difference, with no generated
  consumer of CP0/reset context.

Discriminator: one table listing each candidate field, its retail writer, first
generated read, first generated overwrite, and consumer. A pre-overwrite game
read selects H1; no generated read selects H2; only runtime/host reads select H3.

Exact commands:

```
rg -n -C 5 'CP0|cp0|status|config|reset_type|getOsResetType|osResetType|reset context|reset_context' /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/device/pif /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/device/r4300 ../N64Recomp/RecompiledFuncs lib/N64ModernRuntime/librecomp/src src/main
rg -n -C 5 'getOsResetType|osResetType|reset_type|CP0_STATUS|CP0_CONFIG|cp0_regs|MEM_W\([^)]*(reset|context)' ../N64Recomp/RecompiledFuncs/funcs_*.c
```

Classify every candidate field before choosing the next boundary.
