# Next work unit

HYPOTHESIS-ID: m5-a12-audio-task-done-boundary

Run one complete M5 A12 boundary capture for `waitForMusyXAudioTaskDone` and
the remaining `0x8014974C` spin on the qualified real-audio/LLE route. A11 is
closed for the covered route; do not repeat its wait/slot capture.

Competing hypotheses:

- H-A12-countdown-writer-valid: `musyxSynthFrame` legitimately decrements the
  task countdown to zero and the wait returns; the remaining spin is separate
  and not reached in the target phase.
- H-A12-port-pump-missing: the port reaches the wait with a live countdown,
  but the producer is not scheduled or the wrong field is polled, so the wait
  cap/spin persists without a matching terminal writer.
- H-A12-route-absent: positive controls fire but neither wait arm reaches the
  requested title/hangar phase, so the boundary is unevaluable.

Discriminating measurement: in one rebuilt binary, phase-gate entry, seed,
countdown reads/writes, zero transition, return, cap, and the separate
`0x8014974C` spin; retain whole-RDRAM and port title/hangar controls. In the
retail oracle watch the corresponding countdown/status range and the named
writer PC(s), with whole-RDRAM as its positive control. A named writer -> zero
count -> wait return with no cap selects H-A12-countdown-writer-valid; a valid
entry plus cap/spin and absent or late zero writer, with retail showing the
writer, selects H-A12-port-pump-missing; fired controls with no wait entry
select H-A12-route-absent.

Preparation and run:

1. Read the A12 inventory and current helpers:
   `rg -n -C 8 'waitForMusyXAudioTaskDone|8014974C|WAIT_NOPUMP|countdown|musyxSynthFrame' docs/M5-AUDIO-PLAN.md docs/CURRENT-TRUTH.md src tools ../N64Recomp/RecompiledFuncs`.
2. Add all port countdown/spin fields and all retail watches before building;
   arm a same-run positive control for every instrument.
3. Build once: `cmake --build build --target RogueSquadron64Recomp -j4`.
4. Run one concurrent capture from `build/` using the canonical
   real-audio/LLE/ungated/solo/spin-yield environment and the Rice oracle;
   terminate with SIGKILL, phase-gate on VI transitions, and reject any null
   without title and hangar controls.
