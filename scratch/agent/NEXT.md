# NEXT (s7309): name the drawer of the 21:9 dd>1 left-edge white sliver at the L1 pose-lock freeze k2
HYPOTHESIS-ID: g5f-219-left-sliver
State (s7308): tools/g3_optin_pose_arms.sh PIN=1 at L1 gives pixel-identical repeat captures (floor 0.00). At freeze k2
(x 106.28, open off-map plain) 21:9 dd6/dd8/dd8f show 880-930 near-white (>235) px in the left 1% columns vs dd1 61, and 16:9 shows 0.
See scratch/s7308/a219/dd8/f2_2.png and docs/owner_sheet_s7308_dd8_horizon.jpg (left edge of the 21:9 rows).
Hypotheses:
 H-spike: a knife triangle that escapes CULL_SPIKE (G5f class). Its RDP tri has an extreme-x vertex, and LOG_SPIKE lists it at the k2 frame.
 H-sheet: a W_SHEET guard-band sky-sheet residual at the wide left edge (W_SHEET_PX/POS cull). ROGUESQ_W_SHEET_DROPLOG/STATS show a
   sheet at x<0, and W_SHEET_POS=0 changes the sliver.
 H-rt64: the RDP stream is clean at that column and RT64 draws it (edge clamp / scissor at fbw 1024).
Unit, ONE build (none needed: env only), arms at the same frozen pose (exact cross-run compare):
 env PIN=1 TAGP=s7309 FZ=106.28 zsh tools/g3_optin_pose_arms.sh scratch/s7309/a \
   base=$B+ROGUESQ_DRAW_DISTANCE=8 spk=$B+ROGUESQ_DRAW_DISTANCE=8+ROGUESQ_LOG_SPIKE=1+ROGUESQ_W_SHEET_DROPLOG=1+ROGUESQ_W_SHEET_STATS=1 \
   cs0=$B+ROGUESQ_DRAW_DISTANCE=8+ROGUESQ_CULL_SPIKE=0 wsp0=$B+ROGUESQ_DRAW_DISTANCE=8+ROGUESQ_W_SHEET_POS=0 d1=$B+ROGUESQ_DRAW_DISTANCE=1
 (B as in scratch/s7308/run.zsh with ASPECT=21:9). Score with the left-edge white count in tools/s7308_pose_horizon.py style (add an
 EDGE_WHITE column). Positive control: cs0 must change the spike count (more wedges) and base must reproduce 880+ px.
 Discriminator: the sliver changes in cs0 -> H-spike. It changes in wsp0 -> H-sheet. Neither, and no logged tri reaches x<=0 -> H-rt64
 (then dump RDP with ROGUESQ_S7096_FWD / angrylion replay of that frame).
Needs an unlocked screen and idle host. g3_optin_pose_arms.sh gates on both.
