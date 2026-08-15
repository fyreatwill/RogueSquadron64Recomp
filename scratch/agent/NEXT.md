# NEXT work unit (s1183)

HYPOTHESIS-ID: m3-stack-memory-value-origin

Work unit: complete one static audit of generated `SD`/wide-copy writers and
their host-side RDRAM accessors that could corrupt the shared stack value before
`slotDispatcherIter`. Do not build or run.

Competing hypotheses and discriminator:

- H1: a generated wide store has a reachable mission/cinematic destination
  expression overlapping a target saved-register frame. Discriminator: an
  enumerated `SD`/wide-copy site has both a reachable target-path edge and a
  statically possible frame-overlap span.
- H2: the host accessor broadens a generated wide store into a dynamic RDRAM
  write that can cover the frame. Discriminator: the host implementation or
  call contract permits an unbounded/dynamic destination on a reachable edge.
- H3: all wide-store/accessor classes are frame-local, bounded away, or
  unrelated. Discriminator: no enumerated site has both target-path reachability
  and a destination expression capable of covering the frame.

Exact commands:

```
rg -n 'SD\(|LD\(|MEM_[DQ]\(|wide|copy|memcpy|RDRAM|rdram' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs src lib/N64ModernRuntime --glob '*.c' --glob '*.cpp' --glob '*.h'
rg -n 'slotDispatcherIter|0x8011C8|SD\(|MEM_[DQ]\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
git diff --check
```

Classify every hit as reachable overlapping writer, dynamic but potentially
overlapping writer, unrelated subsystem, bounded-away writer, or
non-executable/commented code. If H1 or H2 is selected, the next unit is one
phase-gated positive-control capture at that exact writer; if H3 is selected,
pivot to the next highest-information static idiom without adding a guard.
