# NEXT work unit (s1179)

HYPOTHESIS-ID: m3-stack-memory-writer-census

Work unit: complete a static, repository-wide audit of the guest stack-memory
writer class feeding the `slotDispatcherIter+872` prologue spill. Do not build
or run. Start from the failing caller's frame range and enumerate every
generated store and host/runtime RDRAM write that can overlap it, then classify
the writer and value source.

Competing hypotheses and discriminator:

- H1: a generated guest store writes the corrupted saved `$ra`/frame word.
  Discriminator: a reachable generated store overlaps the failing frame range
  and has a legitimate or wild value source tied to the crash path.
- H2: a host/runtime RDRAM write overlaps that range. Discriminator: a named
  runtime writer (DMA, memset, or callback-side write) reaches the same bytes;
  compare its address/value contract with the failing frame.
- H3: no writer overlaps the frame range; the apparent prologue fault is an
  invalid frame/value from an earlier guest stack-pointer computation.
  Discriminator: exhaustive generated and runtime write census leaves the
  frame range untouched by stores, requiring a value-origin audit instead.

Exact commands:

```
rg -n 'slotDispatcherIter|0x8003E8DC|sw |sh |sb |MEM_[WHSB]|memcpy|memset' build src lib/N64ModernRuntime tools
rg -n 'slotDispatcherIter|0x8003E8DC|sw |sh |sb |MEM_[WHSB]|memcpy|memset' RecompiledFuncs E:/Projects/N64Recomp/RecompiledFuncs  # use whichever generated tree exists
git diff --check
```

Classify every hit into frame-overlap writer, unrelated guest memory, host
runtime write, or non-executable/commented code. Record the complete result
and selected H1/H2/H3 outcome in CURRENT-TRUTH and the ledger. If H1 or H2 is
selected, the next unit is one phase-gated, positive-control runtime capture
at that exact writer; if H3 is selected, audit the earlier `$sp` value origin
without adding a guard.
