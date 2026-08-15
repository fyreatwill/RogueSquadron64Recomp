# NEXT work unit (s1184)

HYPOTHESIS-ID: m3-stack-memory-value-origin

Work unit: complete one static audit of generated `do_swl`/`do_swr` partial
stores and their host-side RDRAM accessors that could corrupt the shared stack
value before `slotDispatcherIter`. Do not build or run.

Competing hypotheses and discriminator:

- H1: a reachable generated partial-store pair writes a mission/cinematic
  destination overlapping a target saved-register frame. Discriminator: an
  enumerated pair has a target-path edge and a destination expression whose
  byte span can overlap that frame.
- H2: the host implementation of a partial store broadens the generated
  address or write span enough to cover the frame. Discriminator: its accessor
  contract writes outside the guest-aligned byte range specified by the MIPS
  operation.
- H3: all partial-store pairs are frame-local, bounded away, unrelated, or
  non-executable. Discriminator: no enumerated pair has both target-path
  reachability and a frame-overlap span, and the host accessor preserves the
  specified byte range.

Exact commands:

```
rg -n 'do_swl|do_swr|do_sdl|do_sdr|SWL|SWR|SDL|SDR' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs src lib/N64ModernRuntime --glob '*.c' --glob '*.cpp' --glob '*.h'
rg -n -C 3 'slotDispatcherIter|do_swl|do_swr' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n -A80 'static inline .*do_swl|static inline .*do_swr|do_swl\(' lib/N64ModernRuntime/N64Recomp/include/recomp.h lib/N64ModernRuntime/N64Recomp/src /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob '*.h' --glob '*.cpp' --glob '*.c'
git diff --check
```

Classify every hit as reachable overlapping writer, dynamic but potentially
overlapping writer, unrelated subsystem, bounded-away writer, or
non-executable/commented code. If H1 or H2 is selected, the next unit is one
phase-gated positive-control capture at that exact writer; if H3 is selected,
pivot to the next highest-information static idiom without adding a guard.
