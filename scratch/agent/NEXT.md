# NEXT: resume qualification of the phase-6 red source transition
HYPOTHESIS-ID: g3c-owner-visual

s6339 completed the exact-lane host-order discriminator. It recorded 128
bounded rows, all `rsp_dmem_to_rdram`; sampled red lanes were already red in
`before=` and changed in `after=`, so these were later overwrites, not the red
source. The VTX, guest-store, bulk, source-red, ordinary-store controls and
130-second DD3 hold all passed.

This is a retry checkpoint: do not rerun or rebuild in the checkpoint iteration.
The existing witness is in the dirty vendored runtime/RT64 tree and the prior
run artifacts are in the s6339 soak output. Resume by adding the source-
transition table described below, then use the exact build and run commands
that follow.

Competing hypotheses: H-unlogged-bulk (the red transition occurs in an earlier
bulk/source path not joined by the current post-VTX witness), H-vtx-copy (the
transition occurs in VTX source/read ordering), and H-host-order-residual (the
bounded sample missed the actual host event). The discriminator is one phase-6
source-transition table: for every joined red lane, capture bytes at range
registration, every intervening exact-range DMA payload/API, and bytes at VTX
read; a pre-VTX red transition selects H-unlogged-bulk, a transition only at
VTX read selects H-vtx-copy, and a matching host payload outside the current
bounded rows selects H-host-order-residual. Retain all existing controls.

Next work unit: add that bounded source-transition witness in the existing F5
VTX/bulk instrumentation, then build and run:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' XENV_EXTRA='ROGUESQ_DD_UNSAFE=1 ROGUESQ_DRAW_DISTANCE=3 ROGUESQ_EDGE_FORCE_RED=1 ROGUESQ_LOG_F5_VTX=1 ROGUESQ_LOG_F5_STORE_SHADOW=1 ROGUESQ_LOG_M5_HOST_WRITE=1 ROGUESQ_FB_DUMP_EVERY=3 ROGUESQ_FB_DUMP_VI=1' HOLD_S=130 LEVEL=1 TAG_SUFFIX='s6339_sources' zsh scratch/agent/g1_level_coverage_common.zsh`

Do not add a fade/cull mitigation.
