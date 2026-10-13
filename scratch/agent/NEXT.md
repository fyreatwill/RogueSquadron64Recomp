# RESUME — next work unit: qualify callback teardown after duplicate dispatch

HYPOTHESIS-ID: m5-callback-teardown-duplicate-slot

The s4770 ordinal run selected all-live-slot dispatch: slots 1 and 2 both
contained `0x8009123C`, and 7,076 target-slot rows matched 7,076 synth-entry
rows. No dispatcher change is authorized. The next unit is one diagnostic
capture of registration, first-match deregistration, shutdown-call identity,
and the complete four-slot table state, using the existing qualified route.

Competing hypotheses and discriminating measurement:

- H-dereg-first-match: shutdown calls `findAndZeroTableSlotMatching` and
  clears only the first duplicate, leaving slot 2 live afterward.
- H-dereg-all-or-repopulated: shutdown clears both duplicates, or a later
  registration repopulates the second slot.
- H-no-shutdown-route: the target route never reaches the shutdown call, so
  the post-shutdown table cannot explain later synth entries.

DISCRIMINATING MEASUREMENT: one rebuilt default-B40 title/hangar capture with
registration rows, deregistration entry/exit rows, shutdown call ordinals, and
four-slot snapshots joined by phase. The VI-loop and title/hangar controls
must fire. A post-deregistration snapshot showing slot 1 zero and slot 2
`0x8009123C` selects H-dereg-first-match; both zero followed by a registration
selects H-dereg-all-or-repopulated; no shutdown row in the target route
selects H-no-shutdown-route. Do not change deregistration behavior.

Build:

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
```

Add the complete teardown table witness through the canonical fixer and live
generated output, rebuild once, then run from `build/` with SIGKILL cleanup:

```sh
env ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_S4700_CB=1 ROGUESQ_A14_YIELD=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_AUTOPILOT='40:start,44:start,48:start,52:start,56:a,60:a,64:start,68:a' ROGUESQ_AUTOPILOT_STOP_WIDTH=0 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 ROGUESQ_LOG_ALL=1 ./RogueSquadron64Recomp
```
