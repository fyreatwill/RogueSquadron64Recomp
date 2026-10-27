# NEXT: extend the red-source witness across the phase-5 boundary
HYPOTHESIS-ID: g3c-owner-visual

Competing hypotheses:

- H-phase5-guest: a phase-5 guest store creates the red bytes before the
  phase-6 VTX registration.
- H-phase5-bulk: a phase-5 RSP/PI DMA or bulk copy creates them without a
  hooked guest store.
- H-earlier-copy: the bytes are already red at the first phase-5 observation,
  leaving an earlier initialization/copy boundary.

Discriminator: retain each phase-6 VTX range and snapshot it at the first
phase-5 source-range observation, then log all phase-5 exact-range guest-store
and host-DMA events until VTX registration. A phase-5 transition selects the
corresponding guest/bulk writer; no transition selects the earlier boundary.
The ordinary-store, VTX, bulk, and EDGE_FORCE_RED controls must still fire.

Bounded work unit: extend the existing regeneration-preserved F5 VTX/store
shadow. Keep the source-transition output capped at 64 rows and the existing
phase gates. Build and run one arm:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' XENV_EXTRA='ROGUESQ_DD_UNSAFE=1 ROGUESQ_DRAW_DISTANCE=3 ROGUESQ_EDGE_FORCE_RED=1 ROGUESQ_LOG_F5_VTX=1 ROGUESQ_LOG_F5_STORE_SHADOW=1 ROGUESQ_LOG_M5_HOST_WRITE=1 ROGUESQ_FB_DUMP_EVERY=3 ROGUESQ_FB_DUMP_VI=1' HOLD_S=130 LEVEL=1 TAG_SUFFIX='s6341_phase5' zsh scratch/agent/g1_level_coverage_common.zsh`

The run must be judged from `keys.log`, the witness counts, and the bounded
log; if the harness again omits its summary, SIGKILL the explicit game PID
and do not claim the hold completed. Do not add fade/cull mitigation.
