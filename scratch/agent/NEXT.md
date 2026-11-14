# NEXT (s7308): G1c dd8 horizon-in-view owner sheet (dd6 vs dd8 vs dd8+FOG_ALT), 16:9 and 21:9
HYPOTHESIS-ID: g1c-dd8-horizon-look
State (s7307): dd8 auto (px8+R128) and FOG_ALT=1,3,1 both qualified (300 s, 0 crash, 60/s) at 16:9 and 21:9. The s7295
look sheet was single-source: its route window banks under cliffs, so the horizon is mostly off-frame and only one L4 shot
separated dd6 (11% sky band) from dd8 (1%). The owner cannot judge dd8 or the fog from that.
Unit: build a horizon-in-view camera and one sheet. Use ROGUESQ_POSE_LOCK=1 + ROGUESQ_POSE_FREEZE (tools/g3_optin_pose_arms.sh,
needs RAND_TRACE + DEBUG_WRITE) at an L1 and an L4 flight pose looking level toward open ground, or pick later route seconds where
pitch ~0 (check camera pitch from G5G/G3C camera logs). Same pose, arms dd6 / dd8 / dd8+FOG_ALT=1,3,1, 16:9 then 21:9.
Hypotheses: H-dd8-visible (dd8 shows more ground than dd6 at the horizon: sky-band fraction / far-terrain pixel fraction drops);
H-dd8-invisible (fog/haze or the 88-cell visibility limit, s7301, hides the dd8 gain: equal far fraction);
H-fog-hides (FOG_ALT removes the dd8 gain it was meant to soften).
Discriminator: far-terrain pixel fraction in the top band (tools/s7295_dd_look_sheet.py / g5e_edge_score) per arm at the same pose,
with a dd1 arm as positive control (must differ from dd6). Output: docs/owner_sheet_s7308_dd8_horizon.jpg.
Needs an unlocked screen and idle host (check CGSSessionScreenIsLocked); otherwise queue it as a SOAK_NEEDS_IDLE recipe.
