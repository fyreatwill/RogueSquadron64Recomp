# NEXT work unit (s1188)

HYPOTHESIS-ID: m3-stack-memory-value-origin

Work unit: complete one static audit of all generated `MEM_D`/`LD` loads and
their consumers. Do not build or run.

Competing hypotheses and discriminator:

- H1: an `MEM_D`/`LD` load feeds a reachable target-path pointer that later
  writes the saved-register frame. Discriminator: a complete dataflow chain
  from one load reaches a frame-overlapping store.
- H2: the doubleword load/accessor contract creates a wild pointer/value.
  Discriminator: the host operation differs from the guest address, width, or
  alignment semantics.
- H3: all `MEM_D`/`LD` loads are unrelated, bounded, or exact and do not feed
  a frame-overlapping writer. Discriminator: no load-to-frame chain is found
  and the accessor is exact.

Exact commands:

rg -n -E 'MEM_D\(|\bLD\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n -C 8 -E 'MEM_D\(|\bLD\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n -A8 -B4 -E '#define MEM_D|#define LD' lib/N64ModernRuntime/N64Recomp/include/recomp.h include/rsp_dpc_macros.h
git diff --check

Classify every hit as reachable pointer producer, bounded scalar load,
unrelated subsystem, or non-executable/commented code. If H1 or H2 is
selected, the next unit is one phase-gated positive-control capture at the
exact consumer; if H3 is selected, pivot to the next highest-information
static idiom without adding a guard.
