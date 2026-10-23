# NEXT: G1c - fold s6024_g1c_igrid2 / igrid025 from SOAK-RESULTS.md (queued, not yet run by loop as of s6025)
HYPOTHESIS-ID: g1c-draw-distance
LOD table 0x9ECB0 arms (s6023) failed their x0.25 control (+4.9%) => inert on lvl1. 0x9DEAC, FOV also shrink-only.
Remaining: H-grid (int counts 0x137A58/60, igrid arms), H-fade (ROGUESQ_FORCE_FOG in flight), H-farplane.
Fold: awk '/\[g1c\] state=/{s=$2} /\[tricnt\]/{field tri=N, keep >=50, mean per s}' on scratch/agent/m6/g1_lvl1g1cigrid*/run.log. Control: igrid025 must shrink >10%; igrid2 pass = >+10% tri/task; x2 may crash (heap) -> capture site.
If igrid null/void: locate grid alloc (rs_malloc 200*(n/10) at 0x800480BC) and patch the count before allocation; then fog arm.
