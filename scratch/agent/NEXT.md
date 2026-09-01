# NEXT work unit — requalify the s3554 slot-dispatch failure

HYPOTHESIS-ID: m5-slot-dispatch-route-requalification

Run one canonical real-audio/LLE-solo/spin-yield/autopilot capture focused on
`slotDispatcherIter` guest PC `0x80007904`, using the existing regeneration-safe
slot-dispatch table and its caller/entry rows. First enumerate the generated
callers and the exact failing dereference around `0x80007904`; do not change
heap, audio, PCM, image-task, output, or texture records. Session 3556 showed
the old `0x80001B08` report is a stale boundary and the route can reach hangar.

Competing hypotheses and discriminator:

- H-SlotInput: a route-valid capture reaches `0x80007904` with malformed slot
  data and a preceding writer breadcrumb.
- H-SlotLifecycle: slot data is valid, but caller/entry ordinals or phase state
  diverge before the failing consumer.
- H-SlotOverlay: caller and slot data match expected shapes, but the selected
  overlay/function body differs.
- H-SlotCrashAbsent: controls remain live but the s3554 failure does not
  reproduce, making the prior crash route-specific rather than a stable slot
  boundary.

The single discriminator is a phase-scoped joined table containing every known
slot-dispatch caller edge, dispatcher entry, pre-call slot pointer/fields,
post-call result, and first-failure breadcrumb in one build/run. Valid versus
invalid pointer fields split input from lifecycle; matching fields with a
wrong body split overlay; no failure with live controls selects route-specific
absence. Do not add a guard or rewrite a value.

Required census before building:

    rg -n "slotDispatcherIter|0x80007904|80007904|slot-dispatch|slot.*caller" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py src docs
    grep -n '^## Session ' PORTING-STATE.md | tail -15

Build and run from `build/` with the canonical route:

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_SLOT_DISPATCH=1 ROGUESQ_LOG_SLOT_SP_GUARD=1 ROGUESQ_AUTOPILOT='3:start,7:start,11:start,15:a,30:start,45:start,60:a,75:start,90:a' ROGUESQ_AUTOPILOT_STOP_WIDTH=512 ./RogueSquadron64Recomp

Positive controls must visibly fire in the same run: autopilot, VI width
transitions, and the slot-dispatch table. Capture output under
`scratch/agent/soak_results/` and kill the game with SIGKILL only.
