# NEXT: G1c phase 2 close-out — owner contact sheet dd1 / dd4 / dd6-bundle at frozen poses, L1 + L4
HYPOTHESIS-ID: g1c-dd-closeout
Context: s7037 folded the fog-depth off-map cull into ROGUESQ_DRAW_DISTANCE (dd>=6 + DD_WIDEWIN auto-arms OFFMAPCULL=2 K=0.6 H=off; [s7037] log line).
12288 cells (ROGUESQ_DD_POOLX_MAX=6) cost +0.6 ms rsp with no edge-score gain at dd8, so dd6 + bundle is the max useful step. Spec (ITERATION 3c G1c phase 2):
"framebuffer contact sheet the owner can eyeball, same camera, dd1 vs dd-max".
Unit: copy scratch/s7035/run_L4.zsh pose section (tools/g3_optin_pose_arms.sh) to scratch/s7038/, arms on the same frozen poses:
 dd1 (ROGUESQ_DRAW_DISTANCE=1, no DD env), dd4 (21:9 WIDEWIN cap 8192), dd6b (dd6 WIDEWIN cap 10240, NO OFFMAPCULL env -> bundle), dd6off (same + ROGUESQ_DD_OFFMAPCULL=-1),
 plus an A/A repeat of dd6b. L1 (NOREF off, deterministic) then L4 (NOREF: check [posefreeze] pos and score same-path only).
Score: python3 tools/s7032_pose_cull_score.py <dir> --base dd6off --aa dd6b2 --sheet docs/owner_sheet_s7038_dd_closeout_l1.jpg (dd6b vs dd6off must sit at A/A: bundle invisible;
 dd1 vs dd6 must differ: positive control = more far terrain). Also grep run logs for [s7037] (bundle armed in dd6b, absent in dd6off/dd4/dd1).
Hypotheses: H-done (dd6b = dd6off at A/A, dd6 shows clearly more terrain than dd4/dd1) -> close G1c phase 2, offer the owner the one-line command; H-visible (dd6b differs
 from dd6off above A/A on some pose) -> bundle must stay opt-in, revert the auto default; H-nogain (dd6 ~ dd4 by eye) -> recommend dd4 to the owner.
Then: G1c phase 2 closes on the owner's look; next ladder rung per ITERATION 3c.
