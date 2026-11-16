# NEXT (s7481)
HYPOTHESIS-ID: heap-uaf-stores

0. Fold scratch/agent/SOAK-RESULTS.md: s7480_uaf_flight (tools/s7480_uaf_recipe.zsh, LV="7:4 12:4 1:8 10:4", HOLD=220).
   Per-arm line `s7480_uaf_flight arm=... uaf_free= trim_defect= recarve_U= recarve_N= plant_detected= locate_ctl= internal=`.
   - rc 0 (every arm: plant DETECTED, locate_ctl=11, internal>0, uaf_free=0, trim_defect=0) -> class EH CLOSED for all 6 levels flown
     (L1/L4/L7/L10/L12/L15); record it in CURRENT-TRUTH item 1 (EH line) and drop the "flight sweep queued" clause.
   - uaf_free>0 -> a REAL use-after-free store (block still free in its own chain at store time). Read that arm's `[s7480] uaf-store`
     row (pc/fn = writer, blk/n/age) + `[s7480] store-bt` / `free-bt` host chains (= guest call chains: who freed it, who wrote it).
     Name the stale pointer holder, fix the root cause (clear the holder at free, or move the free), rerun the arm.
   - trim_defect>0 -> instrument defect (a malloc did not trim its freed records): fix s7480_trim/s7480_malloc, rerun.
   - control FAIL (rc 3) -> read which of plant/locate_ctl/internal is 0 before trusting any zero.

1. Then pick the next M3 idiom class (ITERATION.md item 3; all owner G5 items await the owner's look): grep-enumerate,
   classify every site, guard or prove dead, close the class. Not yet covered by any class: guest READS of freed blocks
   (EH covers stores only; a read-side twin needs a load hook, apply_s7475_slackwatch.py only patches the s5798 store macro).
   Write a fresh NEXT.md with a NEW HYPOTHESIS-ID.
