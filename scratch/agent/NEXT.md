# Next work unit — measure target-phase callback dispatch cardinality

HYPOTHESIS-ID: m5-callback-dispatch-cardinality

Run one single-arm default-B40 real-audio capture from `build/` with the
compiled `ROGUESQ_LOG_S4700_CB=1` witness plus
`ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_CALLBACK_CENSUS=1`. Keep the validated
title/hangar autopilot and LLE/solo/spin-yield route; avoid `ROGUESQ_LOG_ALL`
and unrelated high-volume probes. Use SIGKILL cleanup.

Competing hypotheses and discriminator:

- H-dispatch-all: duplicate `0x8009123C` slots cause two callback-census or
  synth invocations per retrace while both slots are present.
- H-dispatch-first/live-slot: only one live callback is invoked per retrace,
  and first-match removal reduces the duplicate pair to one.
- H-stale-entry: synth entries continue after the callback-table census no
  longer contains `0x8009123C`, proving a separate stale dispatch source.

DISCRIMINATING MEASUREMENT: in title and hangar phases, compare the callback
census invocation count and synth-entry count against each `s4700-cb`
table snapshot. Two invocations while the duplicate pair is present selects
H-dispatch-all; one selects H-dispatch-first/live-slot; any synth entry after
the table has no `0x8009123C` selects H-stale-entry. The phase transition,
registration, deregistration, and synth-entry rows are positive controls.

Exact build command:

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
```

Exact route variables: `ROGUESQ_LOG_S4700_CB=1 ROGUESQ_LOG_PHASE=1
ROGUESQ_LOG_M5_CALLBACK_CENSUS=1 ROGUESQ_A14_YIELD=1
ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1
ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1 PROBE_PHASE_WIDTH=1024
PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1`.
