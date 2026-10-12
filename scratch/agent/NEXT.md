# Next work unit

HYPOTHESIS-ID: m5-a11-wait-for-any-audio-slot-boundary

Run one complete M5 A11 boundary capture for `waitForAnyAudioSlot` and
`anyAudioSlotActive` on the qualified real-audio/LLE route. Do not repeat the
s4690 retail-entry route-null capture or the closed AI/SDL boundary.

Competing hypotheses:

- H-A11-slot-writer-valid: a named guest status writer publishes the terminal
  slot state (`01/02 -> 00`) before the wait returns; the existing cap is only
  defensive.
- H-A11-port-state-stuck: the port reaches the wait with a legitimate active
  slot, but the producer/reaper or message progress needed to clear it is
  missing, so the cap fires without a matching retail state transition.
- H-A11-route-absent: positive controls fire but neither arm reaches the wait
  in the requested title/hangar phase, making the boundary unevaluable.

Discriminating measurement: in one rebuilt binary, phase-gate both arms on
title `0x00790400/1024` and hangar `0x006AB400/512`; retain whole-RDRAM and
port route controls, wait entry/return/cap rows, slot byte reads, every named
slot/status writer, service/reap entry, and the same-slot ordinal join. Retail
must independently watch the corresponding slot/status bytes and writer PCs.
Writer -> terminal store -> wait return with zero cap rows selects
H-A11-slot-writer-valid; a valid entry plus cap and absent/late terminal store,
with retail showing the terminal writer, selects H-A11-port-state-stuck; fired
controls with no wait entry select H-A11-route-absent.

Preparation and run:

1. Read the A11 inventory and current slot/status helpers:
   `rg -n 'waitForAnyAudioSlot|anyAudioSlotActive|ROGUESQ_WAITFORSLOT|slot.*status|serviceVoicePoolFrame' docs/M5-AUDIO-PLAN.md docs CURRENT-TRUTH.md src tools`.
2. Add all port entry/read/cap/writer fields and all retail watches before the
   build; arm a same-run positive control for every instrument.
3. Build once with `cmake --build build --target RogueSquadron64Recomp -j4`.
4. Run the port from `build/` with the canonical real-audio/LLE/ungated/solo/
   spin-yield environment and run the Rice retail oracle concurrently. Gate on
   VI transitions, terminate both processes with SIGKILL, and reject any null
   whose title/hangar controls are absent.
