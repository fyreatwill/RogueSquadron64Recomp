# Next work unit: requalify the M5 route with a new startup-dependency matrix

HYPOTHESIS-ID: m5-route-startup-dependency

The M3 runtime qualification remains externally blocked: this host has no MIPS
GCC/LD and Clang has no MIPS backend. Do not repeat that target build. Session
4055 qualified declared-real again, but the retail-grounded
`0x800052C4/0x800052C8/0x800052CC` rows were all absent (`seen=0`, `n=0`),
so that class is not a usable producer discriminator.

Competing hypotheses:

- H1: a startup dependency or arm interaction prevents the real route from
  reaching the same target-phase producer path; isolating that dependency will
  make a new arm qualify without changing the zero-payload source signature.
- H2: the declared-real route is target-phase-equivalent but its source is
  legitimately zero; a new arm matrix will preserve both target phases and
  the same zero signature while independent controls remain healthy.
- H3: the route is not target-phase-equivalent under this process topology;
  every new arm will fail or stop before one target phase, leaving the source
  census unevaluable.

Discriminator: build one same-build matrix with declared-real, declared-silent,
and legacy-real arms under one newly varied startup dependency (the matrix
must alter process topology or dependency readiness, not launch order or a
fixed inter-arm gap), while the retail oracle runs concurrently. The positive
control must fire and retail must reach both target VIs. H1 is selected if a
previously failing arm reaches both target phases and changes the declared vs
legacy route outcome; H2 if all qualifying arms reach both phases and retain
the zero signature; H3 if no arm reaches both target phases. Record the exact
dependency variation and do not infer a source null from a pre-target crash.

Commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s4055_m5_route_startup_matrix.sh
grep -nE 'positive-control|origin=0x00790400|origin=0x006ab400|FNV=|nonzero=|CRASH|ABORT|startup-dependency' \
  scratch/agent/s4055_m5_route_startup_matrix/driver.log | tail -240
```

The M3 toolchain dependency remains open until a MIPS host produces
`patches.elf`, `RecompiledPatches/patches.c`, and `PatchesLib`.
