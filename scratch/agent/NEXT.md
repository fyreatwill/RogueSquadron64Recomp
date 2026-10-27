# NEXT: enumerate the later phase-5 writer for the red VTX lanes
HYPOTHESIS-ID: g3c-owner-visual

s6347 resolved the D114 witness: its effective addresses and host RDRAM base
were correct, but its source/post values were pointer/list-shaped and did not
match the red bytes at the later VTX boundary. The remaining question is which
later phase-5 guest store supplies those bytes.

Competing hypotheses:

- H-later-store: a later guest store overlapping `0x735560..0x7355D0` writes
  the red VTX payload.
- H-bulk-or-copy: no ordinary generated store overlaps the transition; a bulk
  copy/DMA or uninstrumented path creates the red bytes.
- H-boundary-order: the store census sees the right range but its event order
  is not comparable to the VTX boundary.

Discriminator: for the same target lanes, log every phase-5 guest store after
the D114 rows with sequence, PC, effective address, source value, pre-store
word, and post-store word, then compare the first later post-value with the
independent VTX-boundary red word. Equality names the legitimate writer;
absence with bulk controls firing selects H-bulk-or-copy; non-monotonic or
post-boundary ordering selects H-boundary-order.

Bounded work unit: extend the regeneration-preserved host store shadow with a
target-range phase-5 census capped at 256 rows, retaining the existing D114
exact rows and positive controls. Build and run one DD3 level-1 arm:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`env ROGUESQ_NO_PKILL=1 ROGUESQ_G1B=1 TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+' XENV_EXTRA='ROGUESQ_DD_UNSAFE=1 ROGUESQ_DRAW_DISTANCE=3 ROGUESQ_EDGE_FORCE_RED=1 ROGUESQ_LOG_F5_VTX=1 ROGUESQ_LOG_F5_STORE_SHADOW=1 ROGUESQ_LOG_M5_HOST_WRITE=1 ROGUESQ_FB_DUMP_EVERY=3 ROGUESQ_FB_DUMP_VI=1' HOLD_S=130 LEVEL=1 TAG_SUFFIX='s6348_phase5_target_stores' zsh scratch/agent/g1_level_coverage_common.zsh`

Judge `keys.log`, all four controls, the target-store rows, and the later
VTX-boundary bytes. Do not add fade/cull mitigation.
