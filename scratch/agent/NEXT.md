# Next work unit: isolate M5 arm startup dependencies in one same-build matrix

HYPOTHESIS-ID: m5-route-arm-isolation

M3 runtime qualification is externally blocked: this host has no MIPS GCC/LD,
Clang has no MIPS backend, and no local toolchain/source tree was found. Do
not repeat the M3 target build here. The prior reversed 7-second stagger left
all port arms pre-target, so isolate arm startup dependencies rather than
trying another launch permutation.

Competing hypotheses:

- H1: a shared startup dependency fails regardless of arm, so isolated arms
  reproduce the pre-target failure.
- H2: one or more arms reach title/hangar when launched alone, proving the
  prior multi-arm schedule caused the route failure.
- H3: an isolated arm reaches a target phase with the established zero-payload
  signature, reopening the consumer/source discriminator for that arm.

Discriminator: run the existing harness in one build with each arm isolated
and the retail control retained; collect title/hangar phase markers, task/SP/
image positive controls, and M5 payload signatures. A target-qualified arm
reopens H3 only if it also shows the zero-payload signature; any pre-target
arm remains unevaluable. Use the existing declared-real, declared-silent,
and legacy-real configurations; do not infer runtime behavior from M3.

Commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
# Extend the harness with an isolation mode: launch one port arm per batch,
# retaining the retail process and the same positive controls.
zsh scratch/agent/run_s4019_m5_route_qualification.sh
grep -nE '\[phase\]|positive-control|m5-|CRASH|ABORT' scratch/agent/<new-run>/*.log | head -240
```

The isolation batches must record the exact arm/phase table and retain the M3
toolchain dependency as open until a MIPS host produces `patches.elf`,
`RecompiledPatches/patches.c`, and `PatchesLib`.
