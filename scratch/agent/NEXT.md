# NEXT: G3 in-flight owner-recipe fidelity on unscored levels (CURRENT-TRUTH item 33)
HYPOTHESIS-ID: g3-owner-recipe-levels
State (s7162): scored at the owner recipe (FPS60 dd4 16:9), all H-equal: L0-L14. At 21:9: L6, L15. Remaining: L16, L17, L18.
Take two per iteration: L16 and L17 next (L18 after, then the optional per-run rect-fit change below).
Hypotheses: H-equal (centre frac med ~0.005-0.01; worst swaps = frame-match lag / fast movers); H-level (fixed-place region with ONE-signed colour diff); H-dd (excess only in far rows = top bands).
Commands (one game at a time; screen unlocked: /usr/sbin/ioreg -n Root -d1 | grep -o 'CGSSessionScreenIsLocked[^,]*' prints nothing when unlocked; ~30 GB free, each run needs ~16 GB transient):
 env RDIR=s7163 zsh tools/s7131_arm.zsh 16 L16 "ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
 grep -ciE 'CRASH|SIGSEGV|SIGBUS|abort' scratch/agent/m6/g1_lvl16s7131L16/run.log
 zsh tools/s7141_post.zsh scratch/s7163 L16 0,9,369,216 46,322 ; rm scratch/s7163/L16.cap
 python3 tools/s7159_regfit.py scratch/s7163 L16 ; zsh tools/s7160_fit_post.zsh scratch/s7163 L16   (sheet docs/owner_sheet_s7163_L16_fidelity.png)
 look at the sheet; then rm -rf scratch/s7163/L16r scratch/s7163/L16.raw scratch/s7163/chunkL16_*; repeat for L17.
If regfit offsets differ from (inner 0,1|1,1 / centre3d 0,1 / radar 1,0 / lives 0,2|1,2), grid-refit before calling H-level.
A worst swap >0.05: check the sheet - craft/bolt offset with identical HUD/terrain = frame-match lag, not a defect.
Owner save rule: no SAVE_FROM; NO_SAVE_WRITE stays. CURRENT-TRUTH ~59 KB (<60000; maintenance trigger close - keep edits net-neutral).
