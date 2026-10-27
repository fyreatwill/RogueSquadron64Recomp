# NEXT: qualify the named pre-VTX writer's actual value and byte lanes
HYPOTHESIS-ID: g3c-owner-visual

s6333 qualified the pre-VTX shadow and bulk control on
`scratch/agent/m6/g1_lvl1s6332_vtxlast/run.log`. Phase-6 VTX ranges had prior
writers, mostly `0x8000D114` (`heapFreeListDequeue`) in phase 5; DMA also
overlapped one range. The generated parity hook passes literal zero, so its
writer value field cannot distinguish a real colour write from a pointer/list
write. The phase-6 source-byte dump is red/nonzero in many words.

Work unit: add a post-store witness for the named `0x8000D114` site (and its
same-function sibling stores if the hook is shared), capturing the actual
register value and exact guest byte lanes. Join those records to the existing
phase-6 VTX ranges; retain ordinary-store, VTX, and bulk controls. Competing
hypotheses: H-colour-writer (actual value writes red bytes into the VTX source),
H-list-writer (the named store only writes a heap/list field and the red source
comes from DMA or another writer), H-bulk (DMA is the population writer), and
H-readback (source is red but the framebuffer remains non-red). Discriminator:
the actual post-store destination/value and VTX join in one run. A matching
red-valued store selects H-colour-writer; a non-red/list-shaped store plus DMA
overlap selects H-list-writer/H-bulk; red source with non-red framebuffer leaves
H-readback. Missing controls invalidate the run.

Commands: update the regeneration-preserved generated-store instrumentation,
`cmake --build build --config Debug --target RogueSquadron64Recomp`, then run:
`env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' XENV_EXTRA='ROGUESQ_DD_UNSAFE=1 ROGUESQ_DRAW_DISTANCE=3 ROGUESQ_EDGE_FORCE_RED=1 ROGUESQ_LOG_F5_VTX=1 ROGUESQ_LOG_F5_STORE_SHADOW=1 ROGUESQ_LOG_M5_HOST_WRITE=1 ROGUESQ_FB_DUMP_EVERY=3 ROGUESQ_FB_DUMP_VI=1' HOLD_S=130 LEVEL=1 TAG_SUFFIX='s6334_vtxvalue' zsh scratch/agent/g1_level_coverage_common.zsh`.
Do not add a fade/cull mitigation.
