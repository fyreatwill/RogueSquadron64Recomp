# NEXT work unit (s1181)

HYPOTHESIS-ID: m3-stack-sp-value-origin

Work unit: complete a static audit of earlier guest value producers that can
poison the shared context before the 72 direct `slotDispatcherIter` callers.
Do not build or run. Enumerate every generated non-prologue `ctx->r29`
assignment and every context-preserving generated call edge, then classify
which sources are reachable from the known mission/cinematic paths.

Competing hypotheses and discriminator:

- H1: an earlier generated function directly overwrites `r29` with a value
  that can reach a target caller. Discriminator: a reachable non-prologue
  assignment has a call-graph path into the target family and lacks a valid
  stack-frame interpretation.
- H2: a generated indirect/context-preserving edge carries a poisoned context
  from an earlier caller. Discriminator: a reachable edge bypasses the normal
  frame restore or passes a distinct context object into the target family.
- H3: all enumerated producers are unrelated, unreachable, or valid frame
  idioms. Discriminator: the complete assignment and edge inventory has no
  reachable invalid producer, requiring a broader guest-memory/value audit.

Exact commands:

```
rg -n 'ctx->r29[[:space:]]*=' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n 'slotDispatcherIter|0x8003E8DC|recomp_context|run_thread_function|run_hook|recomp_trigger_event' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs src lib/N64ModernRuntime/librecomp
git diff --check
```

Classify every hit into valid frame setup, reachable invalid producer,
context-preserving edge, unrelated generated/RSP code, or
non-executable/commented code. Record the complete result and selected H1/H2/H3
outcome in CURRENT-TRUTH and the ledger. If H1 or H2 is selected, the next
unit is one phase-gated positive-control capture at that exact producer; if H3
is selected, audit the broader guest memory/value writer without adding a
guard.
