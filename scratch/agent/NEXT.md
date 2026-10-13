# Next work unit — instrument the actual VI-retrace dispatcher cardinality

HYPOTHESIS-ID: m5-callback-dispatch-cardinality

The s4764 run reached title VI 1024 but crashed in
`musyxSynthFrame_s4562_impl+5808` before hangar. Its `m5-callback-census`
counter only reported table changes (`n=0,1,2`), so it could not discriminate
dispatch cardinality. Do not repeat that table-change-only probe.

Before building, inspect the implementation that walks the four-entry VI
retrace callback table and add one phase-scoped invocation ordinal per slot
dispatch. Include a marked dispatcher-path positive control in the same build;
the run is invalid if that control does not fire. Keep the existing s4700 table
and synth-entry witnesses so the ordinal can be correlated with slot snapshots.

Competing hypotheses and discriminating measurement:

- H-dispatch-all: with duplicate `0x8009123C` entries, two marked dispatch
  ordinals occur per retrace.
- H-dispatch-first/live-slot: only one marked ordinal occurs per retrace.
- H-stale-entry: synth entries continue after the marked table dispatcher has
  no `0x8009123C` slot.

DISCRIMINATING MEASUREMENT: in the first target phase reached, join each
dispatcher ordinal to the immediately preceding four-slot table snapshot and
the sampled `musyxSynthFrame` count. The positive control must visibly fire;
otherwise classify the run as instrument-invalid rather than selecting a
hypothesis. Report the VI phase/crash boundary separately.

Build:

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
```

Route:

```sh
env ROGUESQ_LOG_S4700_CB=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_CALLBACK_CENSUS=1 ROGUESQ_A14_YIELD=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s4765_m5_callback_dispatch 110 0.5
```

Use SIGKILL cleanup. Do not change deregistration or add a mitigation.
