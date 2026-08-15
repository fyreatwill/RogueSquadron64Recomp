# NEXT work unit (s1186)

HYPOTHESIS-ID: m3-stack-memory-value-origin

Work unit: complete one static audit of generated `MEM_W` stores in every
function that directly calls `slotDispatcherIter`. Do not build or run.

Competing hypotheses and discriminator:

- H1: a reachable target-path word store writes a destination overlapping the
  callee's saved-register frame. Discriminator: an enumerated store has a
  target-path edge and a destination expression/span that overlaps that frame.
- H2: the host `MEM_W` accessor broadens or misplaces a generated word store.
  Discriminator: its contract writes outside the computed four-byte guest
  range or applies an address transform beyond the documented KSEG0 mapping.
- H3: all target-path word stores are caller-local, bounded, unrelated, or
  non-executable, and the host accessor is exact. Discriminator: no enumerated
  site has both reachability and frame overlap, while the accessor remains a
  four-byte write at the computed address.

Exact commands:

rg -n -F 'MEM_W(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n -C 4 'slotDispatcherIter|MEM_W\([^;]+\)\s*=' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n -A8 -B4 '#define MEM_W' lib/N64ModernRuntime/N64Recomp/include/recomp.h
git diff --check

Classify every hit as reachable overlapping writer, dynamic but potentially
overlapping writer, unrelated subsystem, bounded-away writer, or
non-executable/commented code. If H1 or H2 is selected, the next unit is one
phase-gated positive-control capture at that exact writer; if H3 is selected,
pivot to the next highest-information static idiom without adding a guard.
