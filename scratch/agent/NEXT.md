# NEXT (s7570)
HYPOTHESIS-ID: retail-chain-simplification

19d: dpc trio s7566, CUT_LIVE s7567, SHADE_ORD_RESET s7568, follow-draw trio s7569 DONE.
Unit: ROGUESQ_S7478_STALECHK vs its parent, the port heap canary (src/main/upstream_compat.cpp; grep -n 'S7478\|canary'
src/main/upstream_compat.cpp; PORTING-STATE grep '^## Session 7478 '). Read what the canary writes/checks and what STALECHK repairs.
Hypotheses: H-dead-parent (canary/stale state never arises at defaults -> STALECHK is dead code), H-confinable (the canary
is diagnostic-only and can be env-gated so STALECHK goes with it), H-interlocked (the canary guards a live heap path; keep both).
Discriminator: offline reachability of the canary write/check at defaults + one runtime witness L1 dd1 default vs STALECHK=0,
counter of stale detections (positive control: a planted stale entry must be detected > 0).
Then G1D_EDGE_CONTENT (parent G1D_EDGE, needs ASPECT 4:3 debrief route). Never flip a default; owner decides.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
Re-run after any lever change: python3 tools/s7557_gq_census.py --write && python3 tools/s7565_comp_chain.py --write --check
Run template: scratch/s7569/run.zsh (g1e_owner_quiet_arms, ALLOW_SLOW).
