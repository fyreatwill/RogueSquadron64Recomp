# NEXT work unit (s1185)

HYPOTHESIS-ID: m3-stack-memory-value-origin

Work unit: complete one static audit of generated narrow stores (MEM_H,
MEM_HU, MEM_B, and MEM_BU) and their host-side RDRAM accessors that could
corrupt the shared stack value before slotDispatcherIter. Do not build or
run.

Competing hypotheses and discriminator:

- H1: a reachable generated narrow-store site writes a mission/cinematic
  destination overlapping a target saved-register frame. Discriminator: an
  enumerated site has a target-path edge and a destination expression whose
  byte span can overlap that frame.
- H2: the host implementation of a narrow store broadens the generated
  address, alignment, or write span enough to cover the frame. Discriminator:
  its accessor contract writes outside the guest byte/halfword range specified
  by the MIPS operation.
- H3: all narrow stores are frame-local, bounded away, unrelated, or
  non-executable, and the host accessors preserve their specified ranges.
  Discriminator: no enumerated site has both target-path reachability and a
  frame-overlap span, while the accessor contracts remain exact.

Exact commands:

rg -n 'MEM_H\(|MEM_HU\(|MEM_B\(|MEM_BU\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n -C 3 'slotDispatcherIter|MEM_H\(|MEM_HU\(|MEM_B\(|MEM_BU\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n -A14 -B4 '#define MEM_H|#define MEM_B|#define MEM_HU|#define MEM_BU' lib/N64ModernRuntime/N64Recomp/include/recomp.h
git diff --check

Classify every hit as reachable overlapping writer, dynamic but potentially
overlapping writer, unrelated subsystem, bounded-away writer, or
non-executable/commented code. If H1 or H2 is selected, the next unit is one
phase-gated positive-control capture at that exact writer; if H3 is selected,
pivot to the next highest-information static idiom without adding a guard.
