# NEXT: retain exact phase-5 boundary writes for red VTX ranges
HYPOTHESIS-ID: g3c-owner-visual

Competing hypotheses:

- H-phase5-guest: a phase-5 guest store creates the red bytes before the
  phase-6 VTX registration.
- H-phase5-bulk: a phase-5 RSP/PI DMA or bulk copy creates them without a
  hooked guest store.
- H-earlier-copy: the bytes are already red at the first retained phase-5
  boundary, leaving an earlier initialization/copy boundary.

Discriminator: retain the last exact-range phase-5 guest-store and host-DMA
events at the phase boundary, then compare their payload bytes with the first
phase-6 VTX registration and read. A red phase-5 payload selects its writer;
no red phase-5 payload leaves the earlier initialization/copy boundary open.
The ordinary-store, VTX, bulk, and EDGE_FORCE_RED controls must still fire.

Bounded work unit: replace the saturated fixed-prefix phase-5 store history
with a ring or boundary snapshot keyed by the eventual VTX ranges. Keep the
source-transition output capped at 64 rows and the existing phase gates. Build
and run one arm:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' XENV_EXTRA='ROGUESQ_DD_UNSAFE=1 ROGUESQ_DRAW_DISTANCE=3 ROGUESQ_EDGE_FORCE_RED=1 ROGUESQ_LOG_F5_VTX=1 ROGUESQ_LOG_F5_STORE_SHADOW=1 ROGUESQ_LOG_M5_HOST_WRITE=1 ROGUESQ_FB_DUMP_EVERY=3 ROGUESQ_FB_DUMP_VI=1' HOLD_S=130 LEVEL=1 TAG_SUFFIX='s6342_phase5_boundary' zsh scratch/agent/g1_level_coverage_common.zsh`

The previous fixed arm qualified the controls and 130-second hold but had
`phase5_store_events=0` because its retained event prefix saturated. The next
run must show a nonzero positive-control boundary row before interpreting a
null. Judge it from `keys.log`, the witness counts, and the bounded log; if the
harness omits its summary, SIGKILL the explicit game PID and do not claim the
hold completed. Do not add fade/cull mitigation.
