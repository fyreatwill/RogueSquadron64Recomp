# NEXT: G3 owner-recipe in-flight fidelity at 21:9, remaining levels (CURRENT-TRUTH item 34)
HYPOTHESIS-ID: g3-owner-recipe-219
State (s7164): 16:9 H-equal on L0-L18 (flight windows). 21:9: only L6 (s7141, centre 0.012) and L15 (0.019) scored. The owner plays on a 21:9 ultrawide.
Hypotheses per level: H-equal (RT64 == angrylion at the retail floor), H-wide (a 21:9-only defect: hole/sky corner/HUD anchor, as s7133-s7136 found on L6),
H-cull (diff explained by the deliberate W_SHEET_PX / W_SHEET_POS / CULL_SPIKE drops: confirm with same-run W_SHEET_ALT=0 + W_SHEET_DROPLOG like s7164), H-lag (dup pframe).
Discriminator: per level, RT64 vs its own same-run angrylion over the flight window: centre frac med, frames >0.05, bands, worst-swap sheets.
Order (one game at a time; screen unlocked check prints nothing: /usr/sbin/ioreg -n Root -d1 | grep -o 'CGSSessionScreenIsLocked[^,]*'):
1. L1, L4 (then L0, L2, L3, ...): tools/s7141_arm.zsh <lvl> <name> "ROGUESQ_ASPECT=21:9 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
   (check s7141 PORTING-STATE entry for its exact post command and CW/CH; s7141_arm writes into scratch/s7141), then tools/s7141_post.zsh <dir> <name> 0,11,469,216 <split>,
   rm the .cap, python3 tools/s7159_regfit.py, then tools/s7160_fit_post.zsh <dir> <name> <rect> (refit with tools/s7163_rectfit.py; SHEET_LABEL is 16:9 in fit_post, edit for 21:9).
   LOOK AT THE SHEET FIRST; menus/medal screens: rescore with --t1 <mach from idx col 2 of the last flight swap>.
2. Any frame with angrylion geometry RT64 lacks: same-run W_SHEET_ALT=0 + ROGUESQ_W_SHEET_DROPLOG=<path>, map drops to swaps via idx mach (bisect), as s7164.
Delete .cap/.raw/<name>r/chunk* after each score (disk ~60 GB free; each run ~16 GB transient). Owner save rule: NO_SAVE_WRITE stays, no SAVE_FROM.
CURRENT-TRUTH ~59 KB (<60000 maintenance trigger): keep edits net-neutral or prune.
