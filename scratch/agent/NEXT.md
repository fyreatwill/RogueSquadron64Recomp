# NEXT: G3 owner-recipe fidelity, mission intro cutscene after the crawl, 16:9 (CURRENT-TRUTH item 36)
HYPOTHESIS-ID: g3-fidelity-intro-cutscene-169
State (s7147): items 27-35 closed (flight L1/L4/L6/L15, hangar, menus, logo, crawl all RT64 == angrylion to the floor). Not yet scored:
the mission intro cutscene that follows the crawl on the s7146 route (Chapter crawl -> mission intro flyby), at the owner's 16:9.
Step 1, one run: env RDIR=s7148 ASP=16:9 SECS=170 FROM=<first swap after the crawl ends; s7146 crawl ran to ~6610, start 6600> EVERY=5
DL=69 DU=38 AP=6:start,11:start,16:start,21:start,25:left,27:start,33:start,40:right,46:left,52:right,58:left,64:a zsh tools/s7146_arm.zsh C1 ""
(check CW/CH/DL/DU and the scoring rect for the 16:9 window first: s7125 used rect 0,9,369,216 for 1360x796; re-derive from cap_C1.txt).
Then tools/s7141_post.zsh scratch/s7148 C1 <rect> <split>; per-phase frac>40 + tools/s7147_joint_fit.py with the FINE grid
(JE step 0.002, JY -3..3) — s7147 showed a coarse grid can fake an x-scale. Delete the .cap after replay (8 GB).
Hypotheses: H-equal (cutscene at the retail floor ~0.01 after one fit); H-cut-diff (a class of cutscene geometry RT64 draws differently:
name it with s7146_opcensus.py on the worst swaps); H-cut-ours (one of our cutscene walkers, DD_CUT_LIVE/s6908 poolmin/s6909 dlreclaim,
changes the stream: both renderers then agree, so check the forwarded stream against the edit census ROGUESQ_S7097_EDIT=ctl).
Discriminator: per-frame frac after fit vs the crawl/flight floor; worst-frame op census.
Owner save rule: no SAVE_FROM; NO_SAVE_WRITE stays. Keep CURRENT-TRUTH under 60000 B (57.8 KB now).
