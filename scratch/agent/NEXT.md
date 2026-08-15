# NEXT work unit (s1193)

HYPOTHESIS-ID: m3-stack-memory-value-origin

Work unit: complete one static audit of every generated `do_sdl`/`do_sdr`
store site. Do not build or run.

The prior iteration was maintenance-only: `CURRENT-TRUTH.md` was compacted
from 619 lines to 140 lines. This work unit is unchanged and is now ready to
run.

Competing hypotheses and discriminator:

- H1: a doubleword partial store reaches a target-path destination that overlaps
  the `slotDispatcherIter` saved-register frame. Discriminator: a complete
  reachable writer edge with a frame-overlapping destination/span.
- H2: the host helper broadens the guest store span or changes the MIPS merge
  contract. Discriminator: helper code reads/writes outside the aligned
  doubleword or differs from the documented merge semantics.
- H3: all sites are bounded, unrelated, malformed, or exact and do not form a
  frame-overlapping writer chain. Discriminator: complete site classification
  finds no H1 edge and an exact helper contract.

Exact commands:

rg -n -e 'do_sdl|do_sdr' /Users/williambuckley/Documents/Tools/N64Recomp --glob '*.{h,hpp,c,cpp,py}'
rg -n -C 10 -e 'do_sdl|do_sdr' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
sed -n '220,264p' /Users/williambuckley/Documents/Tools/N64Recomp/include/recomp.h
git diff --check

Classify all five current generated sites as reachable pointer producer,
bounded scalar/structure store, unrelated subsystem, or non-executable/data-like
code. If H1 or H2 is selected, the next unit is one phase-gated positive-control
capture at the exact consumer; if H3 is selected, continue to the next
highest-information static idiom without adding a guard.
