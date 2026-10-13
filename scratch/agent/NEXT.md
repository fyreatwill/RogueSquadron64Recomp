# Next work unit — qualify the VI-retrace audio callback teardown boundary

HYPOTHESIS-ID: m5-callback-deregistration

Audit the live port path around `shutdownAudioEngine`,
`findAndZeroTableSlotMatching(0x8009123C)`, and the four-slot VI-retrace
callback dispatcher. Build one instrumented binary with phase-scoped counters
for: deregistration call/target/table slot, subsequent callback-table entries,
`musyxSynthFrame` entry after deregistration, and the existing whole-route
phase controls. Run one real-audio capture from `build/` with the validated
LLE/solo/spin-yield configuration and the existing title/hangar key route.
Use SIGKILL cleanup and retain the positive controls.

Competing hypotheses and discriminator:

- H-deregistered: shutdown writes the matching callback slot to zero and the
  dispatcher stops invoking `musyxSynthFrame`; the callback crash is not a
  dispatch-parity defect.
- H-dispatch-stale: the guest deregistration write occurs, but the port
  dispatcher retains or invokes the stale callback; this explains the post-
  teardown synth walk and selects dispatcher parity as the next fix target.
- H-no-deregister: the named guest deregistration path is not reached or does
  not target `0x8009123C`; inspect the writer/phase evidence before changing
  dispatch behavior.

DISCRIMINATING MEASUREMENT: within one run, compare the named deregistration
write and callback-table snapshot against every later `musyxSynthFrame` entry.
Write+zero+no-later-entry selects H-deregistered; write+zero+later-entry
selects H-dispatch-stale; no qualified write selects H-no-deregister. A
whole-RDRAM/phase control must fire before any null is interpreted.

Suggested command shape after the source census:

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
cd build
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 ROGUESQ_LOG_PHASE=1 ./RogueSquadron64Recomp
```
