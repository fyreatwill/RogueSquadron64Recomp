# NEXT: G3 in-flight owner-recipe fidelity on unscored levels (CURRENT-TRUTH item 33)
HYPOTHESIS-ID: g3-owner-recipe-levels
State (s7161): scored at the owner recipe (FPS60 dd4 16:9), all H-equal: L0-L10 L12 L13. At 21:9: L6, L15. Remaining: L11, L14, L16-L18.
Take two per iteration: L11 and L14 next.
Rect: score with the refit 0,10,370,217.
Hypotheses: H-equal (centre frac med at ~0.005-0.01 floor; worst swaps = duplicate-pframe lag); H-level (fixed-place region with ONE-signed colour diff);
H-dd (excess only in far rows = top bands).
Commands (one game at a time; screen unlocked: /usr/sbin/ioreg -n Root -d1 | grep -o 'CGSSessionScreenIsLocked[^,]*' prints nothing when unlocked; ~31 GB free):
 env RDIR=s7162 zsh tools/s7131_arm.zsh 11 L11 "ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
 grep -ciE 'CRASH|SIGSEGV|SIGBUS|abort' scratch/agent/m6/g1_lvl11s7131L11/run.log
 zsh tools/s7141_post.zsh scratch/s7162 L11 0,9,369,216 46,322 ; rm scratch/s7162/L11.cap
 python3 tools/s7159_regfit.py scratch/s7162 L11 ; zsh tools/s7160_fit_post.zsh scratch/s7162 L11   (sheet docs/owner_sheet_s7162_L11_fidelity.png)
 look at the sheet; then rm -rf scratch/s7162/L11r scratch/s7162/L11.raw scratch/s7162/chunkL11_*; repeat for L14.
If regfit offsets differ from (inner 1,1|0,1 / centre3d 0,1 / radar 1,0 / lives 0,2|1,2), grid-refit before calling H-level.
A worst swap >0.05 with dup=1: check the sheet - craft offset with identical HUD/terrain = frame-match lag, not a defect.
Optional bounded change once the sweep is done: make s7122_fidelity score fit the rect per run so the floor stops being registration-limited.
Owner save rule: no SAVE_FROM; NO_SAVE_WRITE stays. CURRENT-TRUTH ~59.0 KB (<60000; maintenance trigger close).
