# NEXT work unit — audit the pre-title audio-slot dispatcher boundary

HYPOTHESIS-ID: m5-audio-slot-dispatcher-boundary

Do one bounded idiom-class audit of `slotDispatcherIter` at guest PC
`0x80007904`, which crashed the canonical route at VI 640 in session 3554.
Before building an instrument, enumerate the generated function and callers,
then inspect the existing audio-slot state layout and independent-oracle
availability. Do not change heap, audio, PCM, image-task, output, or texture
records.

Initial commands:

    rg -n "slotDispatcherIter|0x80007904|waitForAnyAudioSlot|audio.*slot" src lib RecompiledFuncs tools docs
    rg -n "^## Session " PORTING-STATE.md | tail -15
    sed -n '<bounded-hit-window>p' <matching source file>

Competing hypotheses and the discriminator:

- H-DispatcherInput: the dispatcher receives an invalid slot index or state;
  its entry table will show a malformed value before the crashing read, with
  a stable caller and slot-state witness.
- H-DispatcherRoute: the input is valid, but the pre-title route reaches the
  dispatcher in an invalid lifecycle state; entry values are valid while the
  phase/caller sequence differs at the failing iteration.
- H-DispatcherOverlay: the guest PC is executing the wrong overlay/function
  body; a caller/overlay or function-map witness will disagree with the
  expected pre-title dispatch despite valid slot state.
- H-CrashArtifact: the native SIGBUS is unrelated to the guest slot contract;
  the same run reaches the dispatcher positive control but has no stable
  guest-side bad read or route divergence.

The discriminating measurement is one same-build, phase-scoped table covering
dispatcher entry, caller/guest PC, slot index, slot pointer/state, and the
read immediately preceding the crash, plus the existing autopilot and VI
controls. H-DispatcherInput requires a bad slot value; H-DispatcherRoute
requires valid input with a lifecycle/phase mismatch; H-DispatcherOverlay
requires dispatch-body mismatch; absent guest evidence with a live control
selects H-CrashArtifact. A missing positive control invalidates the capture.
Build all fields once, run the canonical real-audio/LLE-solo/spin-yield route
once, and use SIGKILL cleanup from `build/`.
