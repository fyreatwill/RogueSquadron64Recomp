# Next work unit

HYPOTHESIS-ID: m5-a14-status03-shutdown-boundary

Run one complete M5 A14 boundary capture for `shutdownMusyXVoices`, comparing
the current default `ROGUESQ_A14_YIELD=1` arm with the explicit rollback
`ROGUESQ_A14_YIELD=0` arm in one rebuilt binary. A13 is qualified; do not
repeat its drain capture.

Competing hypotheses:

- H-A14-retail-worker-return: both arms reach the status-03 shutdown call in
  the target phase, and the legitimate `serviceVoicePoolFrame` writer clears
  the slot before clean return.
- H-A14-yield-needed: yield-on returns through the worker's status-zero store,
  while yield-off spins or times out; retail independently shows the same
  status-03 writer in the target phase.
- H-A14-route-absent: title/hangar controls fire but neither arm reaches the
  call-3 status-03 boundary, so this boundary is unevaluable.

Discriminating measurement: one binary must phase-gate call-3 entry, status
03 reads, yield arm, named worker entry, exact status-zero stores, shutdown
return, and timeout for both port arms, retaining title/hangar, task/SP, slot
01/02/00, and PCM controls. The retail oracle must use whole-RDRAM, VI,
status-range, adjacent-range, and named writer-PC controls. Writer -> status
03 -> zero -> return in both arms selects H-A14-retail-worker-return;
yield-on-only return with yield-off timeout plus retail writer activity selects
H-A14-yield-needed; positive route controls with no call-3 entry select
H-A14-route-absent. A timeout or clean return without the writer/status chain
is not a result.

Exact preparation and run:

1. Read the A14 inventory and existing anchors:
   `rg -n -C 8 'shutdownMusyXVoices|ROGUESQ_A14_YIELD|status-03|s4296|serviceVoicePoolFrame' docs/M5-AUDIO-PLAN.md docs/CURRENT-TRUTH.md src tools ../N64Recomp/RecompiledFuncs`.
2. Add all A14 fields and retail watches before building; arm positive
   controls for every instrument. Any mitigation-shaped change requires an
   `ORIGIN:` line naming the writer.
3. Build once:
   `cmake --build build --target RogueSquadron64Recomp -j4`.
4. Run both port arms concurrently from `build/`, using the canonical
   real-audio/LLE/ungated/solo/spin-yield environment and phase gates. Run the
   Rice oracle concurrently, terminate every process with SIGKILL, and reject
   any null without title and hangar controls. Save artifacts under
   `scratch/agent/s4694_m5_a14_shutdown_boundary/`.
