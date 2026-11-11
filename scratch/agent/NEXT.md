# NEXT: G3 owner-recipe fidelity, last level L18 + attribute the L17 dark slab (CURRENT-TRUTH item 33)
HYPOTHESIS-ID: g3-owner-recipe-levels
State (s7163): H-equal at 16:9 on L0-L14, L16 flight, L17 flight. At 21:9: L6, L15. Remaining: L18.
Open datum (s7163, single-source): L17 trench swaps 9920-9927, angrylion draws a large dark-grey slab on the right that RT64 does not.
Hypotheses for the slab: H-wsheet (ROGUESQ_W_SHEET_POS drops it, after the cap is recorded), H-spike (CULL_SPIKE drops it), H-rt64 (RT64 itself loses it with both culls off = a real renderer defect), H-lag (frame-match picks a neighbour; refuted if dup 0 holds and the craft is aligned, as in s7163).
Discriminator: per arm, RT64 vs ITS OWN same-run angrylion (no cross-run A/B). A frame showing the slab in angrylion and not in RT64 means a drop in that arm. Slab in both with W_SHEET_POS=0 -> H-wsheet. Same with CULL_SPIKE=0 -> H-spike. Absent from RT64 with both off -> H-rt64.
Order (one game at a time; screen unlocked check: /usr/sbin/ioreg -n Root -d1 | grep -o 'CGSSessionScreenIsLocked[^,]*' prints nothing):
1. L18: env RDIR=s7164 zsh tools/s7131_arm.zsh 18 L18 "ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
   zsh tools/s7141_post.zsh scratch/s7164 L18 0,9,369,216 46,322 ; rm scratch/s7164/L18.cap ; python3 tools/s7159_regfit.py scratch/s7164 L18 ; zsh tools/s7160_fit_post.zsh scratch/s7164 L18
   LOOK AT THE SHEET FIRST. If it shows menus or a medal screen (side frac 1.000 = angrylion magenta side bands), find the flight window. Rescore with
   python3 tools/s7122_fidelity.py score <raw> <idx> <dir>r <out> --rect 0,10,370,217 --split 46,322 --t1 <mach of last flight swap from idx col 2>
   then python3 tools/s7163_rectfit.py <raw> <dir>r <out>.frames.csv 0,10,370,217 and rescore at the best rect. If it is all menu, place FROM by swap (counts agree across runs; L17 flight was 9900).
2. L17 slab arms, same recipe with FROM=9900 plus "ROGUESQ_W_SHEET_POS=0 ROGUESQ_CULL_SPIKE=0" first (one run). If RT64 then draws the slab, run one arm per cull. Score with --t1 at the medal start (L17: first swap with frac_s>0.5). Check frames whose angrylion shows the slab (s7156_sheet.py with chosen swaps).
Delete .cap/.raw/<name>r/chunk* after each score (disk ~30 GB, each run ~16 GB transient). Owner save rule: NO_SAVE_WRITE stays, no SAVE_FROM.
CURRENT-TRUTH ~58.8 KB (<60000 maintenance trigger): keep edits net-neutral.
