# NEXT: qualify the exact-lane host writer/order
HYPOTHESIS-ID: g3c-owner-visual

s6337 completed the post-store discriminator. Controls passed; 2,303/2,308
phase-6 VTX join rows had valid post-values, but no red-valued VTX lane matched
a phase-5 guest-store post-value. The 15 exact matches were zero-valued rows.
The DD3 level-1 hold was alive for 130 seconds with zero VI stalls/crash lines.

Competing hypotheses: H-host-write-order (a host/DMA write populates the red
lane after the last logged guest store), H-unlogged-bulk (a bulk source touches
the exact lane outside the bounded witness), and H-vtx-copy (the red bytes are
produced by a VTX-side copy/read ordering). The discriminator is one exact-lane
host-write table: every host write/DMA event intersecting a joined red VTX lane,
with sequence/API, phase, payload hash/bytes, and RDRAM bytes before/after. A
matching payload selects H-host-write-order; a nonmatching host event followed
by a red transition selects H-unlogged-bulk; no host event plus a red transition
at VTX selects H-vtx-copy. Controls must still fire.

Next work unit: add that bounded host-write ordering witness, retaining the
post-store, VTX, bulk, source-red, and ordinary-store controls. Build and run:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' XENV_EXTRA='ROGUESQ_DD_UNSAFE=1 ROGUESQ_DRAW_DISTANCE=3 ROGUESQ_EDGE_FORCE_RED=1 ROGUESQ_LOG_F5_VTX=1 ROGUESQ_LOG_F5_STORE_SHADOW=1 ROGUESQ_LOG_M5_HOST_WRITE=1 ROGUESQ_FB_DUMP_EVERY=3 ROGUESQ_FB_DUMP_VI=1' HOLD_S=130 LEVEL=1 TAG_SUFFIX='s6337_hostorder' zsh scratch/agent/g1_level_coverage_common.zsh`

Do not add a fade/cull mitigation.
