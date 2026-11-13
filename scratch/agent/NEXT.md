# NEXT (s7234): score the WIDEWIN_R arms (soak s7233b) or run them if the soak voided
HYPOTHESIS-ID: widewin-heavy-window-cost
State: s7233 built ROGUESQ_DD_WIDEWIN_R=<cells> + _R_TOG=1 (skip non-empty cells outside the retail-equivalent 64x64 window farther than
R from the eye). Not yet measured: the r40 arm voided on host sleep. Soak scratch/agent/soak_queue/s7233b_widewin_r.sh queued (R=40,56,72).
Hypotheses (from s7232): H-radius (waste sits in far WW-only cells -> some R cuts sd >=3 ms with kpx loss <0.5%), H-thin (waste spread
over all WW distances -> no R helps without big kpx loss; need coarser far mesh), H-near (cost does not move with R -> governor only).
Step 1: tail SOAK-RESULTS.md. If s7233b rc=0: read scratch/agent/soak_results/s7233b_*.log scorer output. If rc=2 (human/lock/sleep),
check idle (`ioreg -c IOHIDSystem | awk '/HIDIdleTime/{print $NF/1e9; exit}'` >= 120) and lock state, then run the recipe yourself:
`zsh scratch/agent/soak_queue/done/s7233b_widewin_r.sh` (or the queue path if it is still there).
Positive control: [s7233] ph=1 skip > 0 and ph=0 skip = 0, in= equal across phases. Read wide_by_d8 to see where WW-only cells sit.
Outcome: per R, window (t=77-97) dsd and dkpx (Ron - Roff). An R with dsd <= -3 ms and dkpx > -0.5% -> H-radius, then make an owner sheet
(side edge vs docs/owner_sheet_s7009_widewin_219.png, L4 far-left shoreline s7052). All R lose kpx >2% for the gain -> H-thin. dsd ~0 at all R -> H-near.
