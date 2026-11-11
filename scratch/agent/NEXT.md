# NEXT: G3 in-flight owner-recipe fidelity on unscored levels (CURRENT-TRUTH item 33)
HYPOTHESIS-ID: g3-owner-recipe-levels
State (s7156): the G3 menu/cutscene matrix is complete at 21:9 and 16:9 (H-equal everywhere). In flight at the owner recipe (FPS60 dd4
16:9), only L1, L4 (s7131) and L6 (s7125) are scored against angrylion; at 21:9, L6 and L15 (s7141). Remaining: L0, L2, L3, L5, L7-L18
(L10 = cloud level, no terrain grid: still a valid render check). Take two per iteration, most distinct first: L2 (G3b spike-report level)
and L5 (Jade Moon), then L10, L7, L12 (horizon-cut level), L13 ...
Hypotheses: H-equal (frac>40 median at the ~0.01-0.03 floor, outliers = scorer frame-match artefacts, as L1/L4/L6); H-level (a level-specific
material/combiner/texture path RT64 draws differently: a persistent region in the same screen place over many frames); H-dd (diffs only in
extended dd>1 cells, i.e. far rows, while near rows are at the floor).
Commands (one game at a time; ~29 GB free at s7156, each stream ~12.6 GB, delete the .cap right after the replay):
 tools/s7131_arm.zsh hardcodes R=scratch/s7131: add an RDIR env (default s7131) first, as s7146_arm did.
 L2: env RDIR=s7157 zsh tools/s7131_arm.zsh 2 L2 "ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
 Post: zsh tools/s7141_post.zsh scratch/s7157 L2 0,9,369,216 46,322 ; then rm scratch/s7157/L2.cap ; then the same for L5.
 Check FROM lands in flight per level (s7131 used 7500 for L1/L4; look at the run's swap count vs the flight start in run.log). Drop any
 swap whose pframe is clamped to the last raw frame (s7156 capture-tail trap). For outliers, s7143_affine fit + by-eye RT64|angrylion
 sheet (tools/s7156_sheet.py, SHEET_RECT=0,9,369,216 SHEET_LABEL=16:9).
Discriminating outcomes: floor + only frame-match outliers -> H-equal for that level; a fixed-place region repeating over frames -> H-level
(op-census the swap with tools/s7146_opcensus.py, name the op); excess confined to far rows -> H-dd.
Owner save rule: no SAVE_FROM; NO_SAVE_WRITE stays. CURRENT-TRUTH 58.4 KB (<60000).
