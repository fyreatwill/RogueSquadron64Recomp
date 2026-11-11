# NEXT: G3 in-flight owner-recipe fidelity on unscored levels (CURRENT-TRUTH item 33)
HYPOTHESIS-ID: g3-owner-recipe-levels
State (s7157): scored at the owner recipe (FPS60 dd4 16:9), all H-equal: L1, L2, L4, L5, L6. At 21:9: L6, L15. Remaining: L0, L3, L7-L18.
Take two per iteration: L10 (cloud level, no terrain grid) and L7 next, then L12 (horizon-cut), L13 ...
Hypotheses: H-equal (frac>40 median at the ~0.007-0.03 floor; outliers are frame-match lag in fast rolls); H-level (a level-specific
material/combiner path differs: a fixed-place region repeating over many frames); H-dd (excess only in far rows).
Commands (one game at a time; ~25 GB free; each level costs 12.6 GB .cap + 3.2 GB .raw, so delete both after scoring each level):
 env RDIR=s7158 zsh tools/s7131_arm.zsh 10 L10 "ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
 zsh tools/s7141_post.zsh scratch/s7158 L10 0,9,369,216 46,322 ; rm scratch/s7158/L10.cap
 Summarise frames.csv dropping pframe==0 and pframe==max (the s7157 iteration used an tools/s7157_fsum.py <frames.csv>: median/p90/max of meand and frac_over_T,
 count >0.05, centre/side, plus 8 row bands from L10.rows.csv). Sheet: SHEET_RECT=0,9,369,216 SHEET_LABEL=16:9 python3 tools/s7156_sheet.py
 raw aldir frames.csv out.png swaps. Then rm the .raw and r/ dir. Same for L7.
Discriminating outcomes: floor + lag-only outliers -> H-equal; a fixed-place region repeating -> H-level (tools/s7146_opcensus.py on that swap);
excess confined to far rows -> H-dd.
Owner save rule: no SAVE_FROM; NO_SAVE_WRITE stays. CURRENT-TRUTH 58.6 KB (<60000; the next maintenance trigger is close).
