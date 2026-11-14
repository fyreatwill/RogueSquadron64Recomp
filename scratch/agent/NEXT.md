# NEXT (s7311): fold the s7311 FARMAX hold soak, then check the other dd8 levels' sky periphery
HYPOTHESIS-ID: g5f-219-left-sliver
State (s7310): ROGUESQ_DD_FARMAX=32767 default (far plane cap at dd>1) removes the 21:9 left sliver and the warped sky-dome edges at L1.
Threshold far 36.3k-40.4k. Proof is one pose on one level (L1).
1. If SOAK-RESULTS has s7311_219_dd8_farmax_hold: fold it (alive, crashlines, 60/s, "[s7310] far max 32767" in l1/l5/l12, "far max 0" in l1o,
   l1 heaviest20 vs l1o). If it fails, root-cause that arm.
2. Second level/pose (rule 4, widen the evidence): same-pose arms on L5 and L12 (21:9 dd8): FARMAX default vs FARMAX=0, PIN=1, then
   tools/s7310_sliver_score.py on f0_2.png and tools/s7310_left_w.py on the decoded frozen swap (tools/s7310_cap_swaps.py names it).
   Template scratch/s7310/run5.zsh (change FORCE_SAVE_MISSION; FZ pose must be taken from that level's [posefreeze] line, see
   tools/g3_optin_pose_arms.sh). Expect: FARMAX=0 shows pinned W~0 edge tris where the dome reaches the edge, the default shows none.
   If a level shows pinned tris even at 32767, lower the default (bisect as s7310) or make it relative to the dome w.
3. Delete the .cap files after decoding (400 MB each with MAX_MB=400).
Needs an unlocked screen and an idle host (the arms script checks both).
