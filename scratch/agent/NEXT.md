# NEXT work unit (s1180)

HYPOTHESIS-ID: m3-stack-sp-value-origin

Work unit: complete a static audit of the earlier guest `$sp` value origin
feeding the 72 direct `slotDispatcherIter` callers. Do not build or run. Start
from the generated caller entries and enumerate every `$sp` computation/load,
then trace the context-producing edge far enough to classify the invalid-value
source.

Competing hypotheses and discriminator:

- H1: a generated caller computes or loads an invalid `$sp` before the call.
  Discriminator: a reachable caller site has a bad arithmetic/load chain or a
  mismatched context source that can produce the observed frame value.
- H2: a runtime context handoff supplies the invalid `$sp`. Discriminator: a
  named runtime callback/thread/context edge writes or restores `r29` with a
  value outside the guest stack contract.
- H3: all caller and runtime `$sp` producers preserve the contract; the bad
  value is introduced by earlier guest memory/value corruption not resolved by
  this census. Discriminator: the complete producer inventory has no invalid
  arithmetic, load, or context assignment, requiring a broader value-origin
  audit.

Exact commands:

```
rg -n 'slotDispatcherIter|0x8003E8DC|ctx->r29|addiu.*\$sp|addu.*\$sp|lw.*\$sp|MEM_W.*r29' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs src lib/N64ModernRuntime
rg -n 'r29|ctx->r29|recomp_context|run_thread_function|run_hook|recomp_trigger_event' src lib/N64ModernRuntime/librecomp
git diff --check
```

Classify every hit into valid caller frame setup, invalid/mismatched `$sp`
producer, runtime context handoff, unrelated register use, or
non-executable/commented code. Record the complete result and selected H1/H2/H3
outcome in CURRENT-TRUTH and the ledger. If H1 or H2 is selected, the next
unit is one phase-gated positive-control capture at that exact producer; if H3
is selected, audit the earlier guest memory/value producer without adding a
guard.
