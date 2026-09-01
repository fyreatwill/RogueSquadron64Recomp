# M5 Session 3527 — selector mixer caller discriminator

The session-3526 real-audio route was instrumented with a regeneration-safe,
phase-keyed table covering the complete generated caller scope: the sole
`allocateSongChannelArray` call at `0x80091934`, and the two callers of
`initN64RspMixer` at `0x80091C58` (`initAudioSubsystem`) and `0x80091D14`
(`reapplyAudioConfig`). Existing entry, producer-context, selector-store,
mixer-entry, route, and phase controls were retained.

The build completed. The single canonical real-audio/LLE/spin-yield/autopilot
run passed the positive controls and reached title VI 1024 and hangar VI 512.
In hangar, `reapplyAudioConfig` called `initN64RspMixer`, which reached the
sole allocate edge and then `allocateSongChannelArray`; their argument rows
matched at `a0=0x12, a1=0x5622, a2=0, a3=1`. `initAudioSubsystem` had no hangar
row. The existing entry and both selector-store contexts remained live.

This selects `H-StoreCallerParity` for the qualified generated caller scope:
the live route and direct allocate edge are present, so the missing known
display-mode route is not the explanation for the hangar stores. The next
discriminator is a later producer/context edge between the mixer entry and
the selector stores. This is single-source port evidence; no retail oracle
pair was run in this work unit.

ORIGIN: diagnostic-only phase, caller, route, entry, argument, and store
observations. No audio, selector, task, or output state was rewritten.
