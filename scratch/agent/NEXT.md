# NEXT: qualify the bulk/DMA payload and byte lanes
HYPOTHESIS-ID: g3c-owner-visual

s6334 qualified the pre-VTX shadow, VTX, and bulk controls on
`scratch/agent/m6/g1_lvl1s6334_vtxvalue/run.log`. The corrected witness shows
`0x8000D114` writes heap/list pointers, so it is not the colour writer. The
phase-6 source-byte dump is red/nonzero in many words and
`rsp_dmem_to_rdram` overlaps the VTX ranges, but the bulk log currently proves
only range overlap, not that the copied payload contains those red bytes.

Work unit: add a phase-6 bulk/DMA payload witness at the existing
`rsp_dmem_to_rdram` overlap path, recording source physical address, length,
the exact destination lanes, and copied bytes (or a bounded hash plus the
overlapped lane bytes). Join it to the existing VTX ranges; retain ordinary
store, VTX, and bulk controls. Competing hypotheses: H-bulk-colour (the DMA
payload contains the red bytes in the joined lanes), H-other-precopy (the
range overlap is incidental and another guest writer supplies them), and
H-readback (the source is red but the framebuffer remains non-red).
Discriminator: exact copied payload bytes and destination/lane intersection
in one run. Red bytes in the DMA overlap select H-bulk-colour; non-red DMA
with red source selects H-other-precopy; red source with non-red framebuffer
leaves H-readback. Missing controls invalidate the run.

Commands: update the regeneration-preserved bulk instrumentation,
`cmake --build build --config Debug --target RogueSquadron64Recomp`, then run
the same qualified route with `TAG_SUFFIX='s6335_vtxbulkvalue'`:

`env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' XENV_EXTRA='ROGUESQ_DD_UNSAFE=1 ROGUESQ_DRAW_DISTANCE=3 ROGUESQ_EDGE_FORCE_RED=1 ROGUESQ_LOG_F5_VTX=1 ROGUESQ_LOG_F5_STORE_SHADOW=1 ROGUESQ_LOG_M5_HOST_WRITE=1 ROGUESQ_FB_DUMP_EVERY=3 ROGUESQ_FB_DUMP_VI=1' HOLD_S=130 LEVEL=1 TAG_SUFFIX='s6335_vtxbulkvalue' zsh scratch/agent/g1_level_coverage_common.zsh`

Do not add a fade/cull mitigation.
