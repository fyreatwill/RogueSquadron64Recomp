# NEXT work unit (s1182)

HYPOTHESIS-ID: m3-stack-memory-value-origin

Work unit: complete one systematic static audit of broader guest memory/value
writer classes that could corrupt the shared stack value before the 72 direct
`slotDispatcherIter` callers. Do not build or run. Enumerate dynamic writes to
the saved-register/prologue neighborhoods plus generated DMA, zmemcpy,
controller, and flash writers; classify every site as reachable
mission/cinematic writer, unrelated subsystem, or no valid edge.

Competing hypotheses and discriminator:

- H1: a generated writer can reach the failing caller's saved-register frame.
  Discriminator: a complete address/span inventory contains a reachable write
  whose physical span overlaps a target frame and whose value is not a valid
  saved register.
- H2: the writer is dynamic and its address is not statically nameable, but a
  complete writer-class census identifies a reachable DMA/copy path whose
  runtime destination can cover the target frame. Discriminator: the class has
  a proven mission/cinematic edge and an address-producing expression that can
  cover the frame.
- H3: all writer classes are unrelated, bounded away, or legitimate.
  Discriminator: no enumerated writer has both a reachable target-path edge and
  a destination expression capable of covering the failing frame.

Exact commands:

```
rg -n 'MEM_[WBHDQ]\(|zmemcpy|memcpy|DMA|dma|osPiStartDma|controller|flash' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs src lib/N64ModernRuntime --glob '*.c' --glob '*.cpp' --glob '*.h'
rg -n 'slotDispatcherIter|0x8011C8|0x8011C880|0x8011C8C0|rdram\)|MEM_[WBHDQ]' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n 'zmemcpy|memcpy|osPiStartDma|DMA|controller|flash' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
git diff --check
```

Classify every hit into reachable overlapping writer, dynamic but potentially
overlapping writer, unrelated subsystem, bounded-away writer, or
non-executable/commented code. Record the complete result and selected H1/H2/H3
outcome in CURRENT-TRUTH and the ledger. If H1 or H2 is selected, the next
unit is one phase-gated positive-control capture at that exact writer; if H3
is selected, pivot to the next highest-information static idiom class without
adding a guard.
