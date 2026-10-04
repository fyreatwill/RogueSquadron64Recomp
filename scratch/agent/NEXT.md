# Next work unit: validate the accumulated M3 heap patch

HYPOTHESIS-ID: m3-heap-patch-pipeline

The last work unit added the early active-queue ownership guard in
`patches/heap_guards.c`. First determine whether the configured tree can build
the accumulated patch; do not add another guard if it cannot.

Competing hypotheses:

- H1: the patch pipeline is configured and can compile/link the accumulated
  MIPS guard for runtime qualification.
- H2: the patch target is absent or the MIPS toolchain is unavailable, so no
  runtime claim is possible.
- H3: the patch build fails for a new source/link reason that needs repair.

Discriminator: `cmake --build build --config Debug --target PatchesLib` must
either produce the target and its generated patch artifact (H1), report the
known missing target/toolchain boundary (H2), or show a new actionable build
failure (H3). The ordinary host build is a secondary control only.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    cmake --build build --config Debug --target PatchesLib

If H1 is selected, inspect the generated patch artifact and run the existing
patch-qualified route. If H2 repeats, stop the M3 campaign and return to the
M5 candidate census only after recording that external dependency; do not add
another unqualified guard.
