# NEXT (s7483)
HYPOTHESIS-ID: g1d-retarget-unreserved-pool

s7482 fixed item 1a: ROGUESQ_RETARGET_RESERVE (default on) lowers partitionFramebufferMemory's returned $v1 from ec to the
retarget pool base. Same-build A/B on L7: loc_S 151 -> 0, 0 collisions. Two gaps remain before closing the item:

1. Fold soak s7482_reserve_levels (L4/L12 dd4, L1/L15 dd8 21:9) from SOAK-RESULTS. Pass = rc 0. Count per arm whether
   `[s7482] reserve applied` fired at all (if 0 on a level, the retarget never took "ok" there and the arm is coverage only).
2. Hangar abort/re-entry route under the default (RESERVE on): the s7468/s7469 route recipe (grep SOAK-RESULTS s7468_asan_uc_routes,
   find its script in scratch/agent/soak_queue/done/) with ROGUESQ_S7482_CTL=1 and ROGUESQ_LOG_G1D_TASK unset. Hypotheses:
   H-route-clean (alive, 0 pool-collide, menu frames normal) vs H-route-shrink (the heap lost 0x4B000 at the re-entry carve and an
   rs_malloc fails / spills: grep `[s6569]` spill lines and rs_malloc NULL returns vs a RESERVE=0 arm in the same invocation).
   Build both arms in one invocation (LV third field or arm env).
If both pass: close item 1a in CURRENT-TRUTH, change the HYPOTHESIS-ID and take the next ladder item (CURRENT-TRUTH Next steps).
