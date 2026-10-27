# RESUME: audit the exact phase-5 store address/readback witness
HYPOTHESIS-ID: g3c-owner-visual

Checkpoint close-out: do not rerun the interrupted work in this iteration.
The available s6345 run is qualified and non-discriminating: the phase-5
boundary snapshot found red bytes before VTX, while the retained
`0x8000D114` source/post-store values were pointer/list-shaped and did not
match those bytes. Resume by building the exact-address witness below.

The s6345 phase-boundary fallback found red bytes already present in phase 5,
but the matching `0x8000D114` source values and post-store readbacks were
pointer/list values, not the actual red VTX words. Do not call that PC the
colour writer until the witness is reconciled.

Competing hypotheses:

- H-real-store: the generated `0x8000D114` store writes the VTX lane and the
  post-store hook is reading the wrong endian/address representation.
- H-wrong-address: the hook's effective address or register extraction points
  at a different guest location than the boundary row.
- H-wrong-buffer: the post hook reads a stale/different host RDRAM base while
  the VTX join reads the live buffer.

Discriminator: for the same phase-5 `0x735560..0x7355D0` lanes, log one
bounded row containing the generated store's effective address, source value,
pre-store bytes, post-store bytes, the post-hook base identity, and the later
VTX-boundary bytes. Equality of post-store and boundary bytes selects
H-real-store; a different effective address or base selects H-wrong-address or
H-wrong-buffer. The ordinary-store and VTX controls must fire in the same run.

Bounded work unit: extend the regeneration-preserved D114 post-store witness
and host helper with those exact fields, capped at 64 rows; keep the phase-5
snapshot fallback and all existing positive controls. Build and run one arm:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' XENV_EXTRA='ROGUESQ_DD_UNSAFE=1 ROGUESQ_DRAW_DISTANCE=3 ROGUESQ_EDGE_FORCE_RED=1 ROGUESQ_LOG_F5_VTX=1 ROGUESQ_LOG_F5_STORE_SHADOW=1 ROGUESQ_LOG_M5_HOST_WRITE=1 ROGUESQ_FB_DUMP_EVERY=3 ROGUESQ_FB_DUMP_VI=1' HOLD_S=130 LEVEL=1 TAG_SUFFIX='s6346_d114_exact' zsh scratch/agent/g1_level_coverage_common.zsh`

Judge from `keys.log`, the four control markers, and the bounded exact-store
rows. Do not add fade/cull mitigation.
