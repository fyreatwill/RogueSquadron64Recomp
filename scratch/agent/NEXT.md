# Next work unit: run concurrent diagnostic-isolation arms

HYPOTHESIS-ID: m5-diagnostic-launch-order-interaction

s3808 ran the planned sequential six-arm matrix. The independent retail oracle
fired its whole-RDRAM control 10,000 times and reached title/hangar. Minimal,
LOG_PHASE, PCM-boundary, and B40 failed before target; audio-return and
route-state reached only 640; all-five reached title/hangar without a crash.
The all-five bundle is therefore not sufficient to cause the failure in this
run, and the sequential order is confounded.

Competing hypotheses and discriminator:

- H1: one specific variable destabilizes startup; that arm fails in a
  concurrent run while peer single-variable arms reach target.
- H2: launch order/overlap is the cause; concurrent arms change the failure
  pattern relative to sequential arms.
- H3: startup is nondeterministic or unrelated; concurrent arms remain mixed
  without a stable variable or order split.

The discriminating measurement is one same-build concurrent image matrix with
the same six arms and the independent retail oracle. Start all port arms from
the same wrapper before waiting on any one arm. Require the oracle whole-RDRAM
control and title/hangar VIs; for each port arm record target VIs,
crash/abort counts, and last guest PC. Do not add M5 source census fields.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_m5_diagnostic_isolation_concurrent.sh
