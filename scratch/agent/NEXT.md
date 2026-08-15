# NEXT work unit (s1187)

HYPOTHESIS-ID: m3-stack-memory-value-origin

Work unit: complete one static audit of all five generated `MEM_WU` loads and
their consumers. Do not build or run.

Competing hypotheses and discriminator:

- H1: a `MEM_WU` load feeds a reachable target-path pointer that later writes
  the saved-register frame. Discriminator: a complete dataflow chain from one
  of the five loads reaches a frame-overlapping store.
- H2: a `MEM_WU` load is misaddressed by its host accessor and creates a wild
  pointer/value. Discriminator: the accessor contract differs from the
  computed four-byte guest address or KSEG0 mapping.
- H3: all five loads are unrelated, bounded, or exact and do not feed a
  frame-overlapping writer. Discriminator: no load-to-frame writer chain is
  found and the accessor is exact.

Exact commands:

rg -n -F 'MEM_WU(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n -C 8 'MEM_WU\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n -A8 -B4 '#define MEM_W' lib/N64ModernRuntime/N64Recomp/include/recomp.h
git diff --check

Classify every hit as reachable pointer producer, bounded scalar load,
unrelated subsystem, or non-executable/commented code. If H1 or H2 is
selected, the next unit is one phase-gated positive-control capture at the
exact consumer; if H3 is selected, pivot to the next highest-information
static idiom without adding a guard.
