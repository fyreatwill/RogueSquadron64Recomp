# NEXT: G3 in-flight owner-recipe fidelity on unscored levels (CURRENT-TRUTH item 33)
HYPOTHESIS-ID: g3-owner-recipe-levels
State (s7158): scored at the owner recipe (FPS60 dd4 16:9), all H-equal: L1, L2, L4, L5, L6, L7, L10. At 21:9: L6, L15. Remaining: L0, L3, L8, L9, L11-L18.
Take two per iteration: L12 (horizon-cut) and L13 next, then L0, L3 ...
Hypotheses: H-equal (frac>40 median at the ~0.007-0.01 floor; outliers are frame-match lag, check for a duplicate pframe on the worst swap);
H-level (a level-specific material/combiner path differs: a fixed-place region repeating over many frames); H-dd (excess only in far rows).
Commands (one game at a time; check screen unlock: /usr/sbin/ioreg -n Root -d1 | grep CGSSessionScreenIsLocked; ~32 GB free; delete .cap after post, .raw + <N>r after sheet):
 env RDIR=s7159 zsh tools/s7131_arm.zsh 12 L12 "ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
 grep -ciE 'CRASH|SIGSEGV|SIGBUS|abort' scratch/agent/m6/g1_lvl12s7131L12/run.log
 zsh tools/s7141_post.zsh scratch/s7159 L12 0,9,369,216 46,322 ; rm scratch/s7159/L12.cap
 python3 tools/s7157_fsum.py scratch/s7159/L12.frames.csv   (and _sh2)
 8 row bands: average L12.rows.csv (one row per pixel row, 207 rows) into 8 equal bands.
 Sheet: env SHEET_RECT=0,9,369,216 SHEET_LABEL=16:9 python3 tools/s7156_sheet.py raw <N>r frames.csv out.png worst,median,p20 swaps
Discriminating outcomes: floor + lag-only outliers -> H-equal; a fixed-place region repeating -> H-level (tools/s7146_opcensus.py on that swap);
excess confined to far rows -> H-dd.
Owner save rule: no SAVE_FROM; NO_SAVE_WRITE stays. CURRENT-TRUTH ~58.7 KB (<60000; the next maintenance trigger is close).
