# Next work unit

HYPOTHESIS-ID: m5-a13-drain-return-boundary

Run one complete M5 A13 boundary capture for
`drainAudioAndFinalizeSpeechBuffer`, comparing the default-off in-loop tick
with the explicit `ROGUESQ_DRAIN_INLOOP_TICK=1` control in one rebuilt binary.
A12 is qualified for the covered route; do not repeat its wait capture.

Competing hypotheses:

- H-A13-retail-status-reap: the drain returns because legitimate slot-status
  writers clear the active slots; default-off and tick-on both show writer ->
  terminal status -> clean drain return, with no timeout.
- H-A13-port-tick-needed: the default port drain stalls or times out because
  its in-loop producer is absent, while the tick-on arm returns and retail
  independently shows the status writer in the same phase.
- H-A13-route-absent: title/hangar controls fire but neither arm enters the
  drain in the requested phase, so this boundary is unevaluable.

Discriminating measurement: one binary must log both arms' phase-gated drain
entry, active-slot reads, status writes, return, and timeout, while retaining
task/SP completion, slot `01/02/00`, and PCM controls. The retail oracle must
watch the corresponding status range and named writer PCs, with whole-RDRAM,
VI, and adjacent-range controls. Writer -> terminal status -> return in both
arms selects H-A13-retail-status-reap; default timeout/absence with tick-on
return plus retail writer activity selects H-A13-port-tick-needed; fired
controls with no drain entry select H-A13-route-absent. A timeout or clean
return alone is not a result.

Preparation and run:

1. Read the A13 inventory and helpers:
   `rg -n -C 8 'drainAudioAndFinalizeSpeechBuffer|DRAIN_INLOOP_TICK|drain-inloop|anyAudioSlotActive|status' docs/M5-AUDIO-PLAN.md docs/CURRENT-TRUTH.md src tools ../N64Recomp/RecompiledFuncs`.
2. Add all drain/slot/status fields and all retail watches before building;
   arm same-run positive controls for every instrument. Any mitigation-shaped
   change requires an `ORIGIN:` line naming the writer.
3. Build once: `cmake --build build --target RogueSquadron64Recomp -j4`.
4. Run one concurrent capture from `build/` with the canonical
   real-audio/LLE/ungated/solo/spin-yield environment, launching the default
   and tick-on arms from the same binary if the existing arm mechanism allows;
   otherwise use the existing same-run control toggle. Run the Rice oracle,
   phase-gate on VI transitions, terminate with SIGKILL, and reject any null
   without title and hangar controls.
