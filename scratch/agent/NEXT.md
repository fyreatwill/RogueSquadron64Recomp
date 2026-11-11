# NEXT: G3 in-flight owner-recipe fidelity on unscored levels (CURRENT-TRUTH item 33)
HYPOTHESIS-ID: g3-owner-recipe-levels
State (s7159): scored at the owner recipe (FPS60 dd4 16:9), all H-equal: L1 L2 L4 L5 L6 L7 L10 L12 L13. At 21:9: L6, L15. Remaining: L0, L3, L8, L9, L11, L14, L16-L18.
Take two per iteration: L0 and L3 next.
s7159 finding: the fixed rect 0,9,369,216 is ~1% small on every level (radar wants +1 x, lives +2 y). Run tools/s7159_regfit.py BEFORE deleting .raw. If a level is high,
refit the rect (grid over x0 0-2, y0 9-11, x1 369-371, y1 216-218) and rescore with s7122_fidelity.py score --rect before calling H-level.
Hypotheses: H-equal (frac>40 median at the ~0.007-0.01 floor; outliers are frame-match lag with a duplicate or jumping pframe); H-level (a fixed-place region with ONE-signed
colour diff, i.e. filled, not an edge outline); H-dd (excess only in far rows).
Commands (one game at a time; screen unlocked: /usr/sbin/ioreg -n Root -d1 | grep CGSSessionScreenIsLocked; ~31 GB free):
 env RDIR=s7160 zsh tools/s7131_arm.zsh 0 L0 "ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
 grep -ciE 'CRASH|SIGSEGV|SIGBUS|abort' scratch/agent/m6/g1_lvl0s7131L0/run.log
 zsh tools/s7141_post.zsh scratch/s7160 L0 0,9,369,216 46,322 ; rm scratch/s7160/L0.cap
 python3 tools/s7157_fsum.py scratch/s7160/L0.frames.csv ; python3 tools/s7159_regfit.py scratch/s7160 L0
 8 row bands from L0.rows.csv; sheet: env SHEET_RECT=0,9,369,216 SHEET_LABEL=16:9 python3 tools/s7156_sheet.py raw L0r frames.csv out.png worst,median,p20
 then rm -rf L0r L0.raw; repeat for L3.
Optional bounded change once the sweep is done: make s7122_fidelity score fit the rect per run (sub-pixel scale) so the floor stops being registration-limited.
Owner save rule: no SAVE_FROM; NO_SAVE_WRITE stays. CURRENT-TRUTH ~58.9 KB (<60000; the next maintenance trigger is close).
