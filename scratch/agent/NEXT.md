# NEXT (s7235): score the WIDEWIN_R arms (soak s7234_widewin_r) or run them if the host is idle
HYPOTHESIS-ID: widewin-heavy-window-cost
State: knob ROGUESQ_DD_WIDEWIN_R=<cells> + _R_TOG=1 built s7233 (default off). Arms never measured: s7233 voided on host sleep and
s7233b on owner activity. s7234 made the loop idle-gate the recipe (# SOAK_NEEDS_IDLE=180, re-queued on rc=2 up to 5x).
Hypotheses (from s7232): H-radius (waste sits in far WW-only cells -> some R cuts sd >=3 ms with kpx loss <0.5%), H-thin (waste spread
over all WW distances -> no R helps without big kpx loss; need a coarser far mesh), H-near (cost does not move with R -> governor only).
Step 1: tail SOAK-RESULTS.md for s7234_widewin_r. rc=0: read the scorer output at the end of its soak_results log (also scratch/s7233b/).
Still queued / VOID re-queued: check idle (`ioreg -c IOHIDSystem | awk '/HIDIdleTime/{print $NF/1e9; exit}'` >= 180) and lock; if
idle, run `zsh scratch/agent/soak_queue/s7234_widewin_r.sh` yourself (then move it to done/). If the owner is active, do NOT launch
the game: take offline work from CURRENT-TRUTH Next steps (owner-look items need nothing from you) and leave the soak to the loop.
Positive control: [s7233] ph=1 skip > 0 and ph=0 skip = 0, in= equal across phases. Read wide_by_d8 to see where WW-only cells sit.
Outcome: per R, window (t=77-97) dsd and dkpx (Ron - Roff). An R with dsd <= -3 ms and dkpx > -0.5% -> H-radius, then an owner sheet
(side edge vs docs/owner_sheet_s7009_widewin_219.png, L4 far-left shoreline s7052). All R lose kpx >2% for the gain -> H-thin. dsd ~0 -> H-near.
