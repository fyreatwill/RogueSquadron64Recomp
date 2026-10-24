# NEXT: G1d step 31 - 12 MB frame verify, then 21:9/16:9 at 12 MB
HYPOTHESIS-ID: g1d-widescreen
Known (s6138): rsp.hpp DMEM->RDRAM write bound fixed; 12 MB RDP list matches 8 MB; task cost normal.
Hypotheses: H-ok (12 MB flight frame correct and heap deficit gone => wide aspect works with OSMEM=12), H-other-cap (remaining >8 MB drop elsewhere: garbage frame, check ROGUESQ_FB_DUMP_VI=1 frame vs 8 MB), H-heap-still (wide heap NULL persists).
Discriminator: scratch/agent/s6138_run.sh arms + ROGUESQ_FB_DUMP_VI=1 for mb8/mb12 (compare dumps visually: terrain/craft/HUD); then arms ROGUESQ_OSMEM_MB=12 ROGUESQ_ASPECT=21:9 and 16:9 on L1 via g1_level_coverage_common.zsh, HOLD_S=300, read alive_at_end and [heapwalk-top]. Positive control: the 4:3 12 MB arm in the same batch.
Then: HUD x anchoring, menus/hangar at wide, default OSMEM bundling under ROGUESQ_ASPECT.
