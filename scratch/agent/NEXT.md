# Next work unit: requalify the M5 route with a new same-build arm matrix

HYPOTHESIS-ID: m5-route-launch-order-gap

M3 runtime qualification is externally blocked: this host has no MIPS GCC/LD,
Clang has no MIPS backend, and no local toolchain/source tree was found. Do
not repeat the M3 target build here. Use the existing M5 route harness, keeping
all arms in one build/run and phase-gating on VI transitions.

Competing hypotheses:

- H1: launch order/gap changes which port arm reaches title `1024` and hangar
  `512`, selecting a schedule discriminator.
- H2: all qualifying arms retain matching zero source/consumer payloads, so
  route reachability is independent of the unresolved producer.
- H3: a port arm fails before either target phase; its source-writer nulls are
  unevaluable and must not advance the writer census.

Discriminator: run a genuinely new launch-order or inter-arm gap matrix based
on `scratch/agent/run_s4019_m5_route_qualification.sh`, with positive controls
for task dispatch, SP completion, image completion, title VI, and hangar VI.
H1 is selected only if arm reachability changes with the schedule; H2 requires
all target-qualified arms to show the same zero payload signature; H3 applies
to any arm missing a target phase. Use `ROGUESQ_AUDIO_UCODE=1` for real-image
arms, `=0` for the silent control, and retain the declared-size/legacy-size
pair. Do not infer runtime behavior from the unavailable M3 patch target.

Commands:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s4019_m5_route_qualification.sh
grep -nE '\[phase\]|audtask|SP|image|hangar|CRASH' scratch/agent/<new-run>/run.log | head -200
```

The new matrix must not be one of the already-tested one-, two-, three-, or
four-second permutations. Record the exact arm/phase table and retain the M3
toolchain dependency as open until a MIPS host produces `patches.elf`,
`RecompiledPatches/patches.c`, and `PatchesLib`.
