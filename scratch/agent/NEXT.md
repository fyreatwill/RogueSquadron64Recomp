# RESUME NEXT: qualify the actual pre-VTX byte writer
HYPOTHESIS-ID: g3c-owner-visual

s6335 already ran the exact DMA-lane witness. Its controls passed, the DD3
level-1 hold survived 130 seconds, and the overlapping DMA bytes did not match
the red bytes later consumed by F5 VTX. This retry only recorded that partial
result; no new run was made.

Competing hypotheses remain: H-guest-store (a phase-5 guest store writes the
red bytes, but the old shadow value was stale/zero), H-host-write-order (a
different host write populates the range after the logged store), and
H-readback (the source is red before VTX but is transformed or lost after VTX).
The discriminator is actual post-store byte readback for every phase-5 guest
store that joins a phase-6 VTX lane. An exact match selects H-guest-store; no
match plus a host-write overlap selects H-host-write-order; a match that is
lost before rendering supports H-readback. Missing controls invalidate the run.

RESUME work unit: extend the regeneration-preserved F5 store shadow to read
the actual post-store 4/8-byte guest-RDRAM value for candidate phase-5 stores,
retain writer PC/address/width and phase, and print bounded joins to phase-6
VTX ranges. Keep the exact DMA payload witness and all controls. After the
instrument edit, run exactly:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Then use the qualified route with a new `s6336` tag:

`env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' XENV_EXTRA='ROGUESQ_DD_UNSAFE=1 ROGUESQ_DRAW_DISTANCE=3 ROGUESQ_EDGE_FORCE_RED=1 ROGUESQ_LOG_F5_VTX=1 ROGUESQ_LOG_F5_STORE_SHADOW=1 ROGUESQ_LOG_M5_HOST_WRITE=1 ROGUESQ_FB_DUMP_EVERY=3 ROGUESQ_FB_DUMP_VI=1' HOLD_S=130 LEVEL=1 TAG_SUFFIX='s6336_vtxpoststore' zsh scratch/agent/g1_level_coverage_common.zsh`

Do not add a fade/cull mitigation.
