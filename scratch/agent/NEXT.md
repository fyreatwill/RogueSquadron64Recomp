# Next work unit: isolate the common M5 launch environment

HYPOTHESIS-ID: m5-diagnostic-load-startup

s3806 ran a fixed same-build image matrix: no census, source/input census, and
full census. The oracle passed its whole-RDRAM control and reached title/hangar;
all three port bundles crashed before title at guest PC `0x8000834C`, with zero
target VI and zero M5 rows. This selects a common launch/diagnostic environment
at this scope; the census category remains unevaluable.

Competing hypotheses and discriminator:

- H1: the census category is the cause; both minimal and current-base arms
  remain unstable because the category is not isolated.
- H2: a common base diagnostic/launch environment destabilizes startup; a
  minimal route arm reaches target while the current-base arm crashes.
- H3: the crash is nondeterministic or unrelated; minimal and current-base arms
  have mixed outcomes without a stable split.

The discriminating measurement is one same-build image-only matrix with two
bundles under the same recipe: a minimal route arm containing only the
validated LLE/audio/phase-driving environment and a current-base arm retaining
the route and passive diagnostics, plus the independent retail oracle. Require
the oracle whole-RDRAM control and target-VI controls. Do not infer a writer or
payload parity from a missing target phase.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_m5_minimal_route_matrix.sh
