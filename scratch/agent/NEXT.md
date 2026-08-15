# NEXT work unit (s1191)

HYPOTHESIS-ID: m3-stack-memory-value-origin

Work unit: complete one static audit of the next distinct generated partial
load/store idiom after `do_lwl`/`do_lwr`, using the current generator/runtime
source to enumerate it and its consumers. Do not build or run.

Competing hypotheses and discriminator:

- H1: the next idiom feeds a reachable target-path pointer that later writes
  the saved-register frame. Discriminator: a complete chain from one
  enumerated load reaches a frame-overlapping store.
- H2: its host helper or merge contract broadens the guest access or creates a
  wild value. Discriminator: helper code reads outside the documented guest
  span or differs from the MIPS merge semantics.
- H3: all sites are bounded, unrelated, malformed, or exact and do not feed a
  frame-overlapping writer. Discriminator: no load-to-frame chain is found and
  the helper contract is exact.

Exact commands:

rg -n -e 'MEM_LWL|MEM_LWR|do_lwl|do_lwr' /Users/williambuckley/Documents/Tools/N64Recomp --glob '*.{h,hpp,c,cpp,py}'
rg -n -C 8 -e 'MEM_LWL|MEM_LWR|do_lwl|do_lwr' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n -A35 -B4 -e 'MEM_LWL|MEM_LWR|do_lwl|do_lwr' /Users/williambuckley/Documents/Tools/N64Recomp/include/recomp.h
git diff --check

Classify every hit as reachable pointer producer, bounded scalar load,
unrelated subsystem, or non-executable/commented code. If H1 or H2 is
selected, the next unit is one phase-gated positive-control capture at the
exact consumer; if H3 is selected, pivot to the next highest-information
static idiom without adding a guard.
