# Next work unit: isolate the startup diagnostic variable

HYPOTHESIS-ID: m5-diagnostic-load-startup

s3807 qualified the common boundary: the independent retail oracle fired its
whole-RDRAM control 10,000 times and reached title/hangar. In the same-build
port matrix, minimal reached title at 49.8s and hangar at 59.7s with no crash;
current-base crashed 36 times before title at guest PC `0x8000834C`. The
minimal route is therefore target-valid, while the current-base diagnostic
bundle is not.

Competing hypotheses and discriminator:

- H1: one specific diagnostic variable destabilizes startup; its single-variable
  arm crashes while the other single-variable arms reach target.
- H2: only the combined diagnostic load destabilizes startup; every
  single-variable arm reaches target but all-base crashes.
- H3: startup remains nondeterministic or unrelated; minimal, single-variable,
  and all-base arms have mixed outcomes without a stable split.

The discriminating measurement is one same-build image matrix containing these
six arms under the same route and input recipe: minimal, `ROGUESQ_LOG_PHASE`,
`ROGUESQ_LOG_AUDIO_RETURN`, `ROGUESQ_LOG_PCM_BOUNDARY`,
`ROGUESQ_LOG_M5_B40_ROUTE`, `ROGUESQ_LOG_M5_ROUTE_STATE`, and all five
together. Run the independent retail oracle concurrently. Require the oracle
whole-RDRAM control and title/hangar VIs; for each port arm record target VIs,
crash/abort counts, and last guest PC. Do not add M5 source census fields.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_m5_diagnostic_isolation_matrix.sh
