# NEXT work unit (s1190)

HYPOTHESIS-ID: m3-stack-memory-value-origin

Work unit: complete one static audit of all generated `do_lwl`/`do_lwr` partial
loads and their consumers. Do not build or run.

Competing hypotheses and discriminator:

- H1: a partial load feeds a reachable target-path pointer that later writes
  the saved-register frame. Discriminator: a complete dataflow chain from one
  `do_ldl`/`do_ldr` result reaches a frame-overlapping store.
- H2: the partial-load helper or its alignment/merge contract creates a wild
  pointer/value. Discriminator: the host helper writes outside the guest
  aligned word or differs from the guest merge semantics.
- H3: all partial loads are bounded, unrelated, or exact and do not feed a
  frame-overlapping writer. Discriminator: no load-to-frame chain is found and
  the helper's address/span behavior is exact.

Exact commands:

rg -n -e 'do_lwl\(|do_lwr\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n -C 8 -e 'do_lwl\(|do_lwr\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n -A35 -B4 -e 'do_lwl|do_lwr' lib/N64ModernRuntime/N64Recomp/include/recomp.h
git diff --check

Classify every hit as reachable pointer producer, bounded scalar load,
unrelated subsystem, or non-executable/commented code. If H1 or H2 is
selected, the next unit is one phase-gated positive-control capture at the
exact consumer; if H3 is selected, pivot to the next highest-information
static idiom without adding a guard.
