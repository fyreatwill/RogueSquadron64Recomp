# NEXT (s7236): score the WIDEWIN_R arms (soak s7235_widewin_r) or run them if the host is idle
HYPOTHESIS-ID: widewin-heavy-window-cost
State: knob ROGUESQ_DD_WIDEWIN_R=<cells> + _R_TOG=1 built s7233 (default off). Arms never measured: s7233 voided on host sleep,
s7233b and s7234 on owner activity (s7234's idle gate was not yet loaded; s7235 fixed loop.sh to re-exec before the soak phase).
Hypotheses (from s7232): H-radius (waste sits in far WW-only cells -> some R cuts sd >=3 ms with kpx loss <0.5%), H-thin (waste spread
over all WW distances -> no R helps without big kpx loss; need a coarser far mesh), H-near (cost does not move with R -> governor only).
Step 0: confirm the gate is live: loop.log should show "re-executing before the soak phase" and either "soak s7235_widewin_r skipped:
host not idle" or a run. A verdict line "rc=2 VOID ... re-queued" also proves it.
Step 1: tail SOAK-RESULTS.md for s7235_widewin_r. rc=0: read the scorer output at the end of its soak_results log (also scratch/s7233b/).
Still queued: check idle (`ioreg -c IOHIDSystem | awk '/HIDIdleTime/{print $NF/1e9; exit}'` >= 180) and lock; if idle, run
`zsh scratch/agent/soak_queue/s7235_widewin_r.sh` yourself (then move it to done/). If the owner is active, do NOT launch
the game: take offline work from CURRENT-TRUTH Next steps and leave the soak to the loop.
Positive control: [s7233] ph=1 skip > 0 and ph=0 skip = 0, in= equal across phases. Read wide_by_d8 to see where WW-only cells sit.
Outcome: per R, window (t=77-97) dsd and dkpx (Ron - Roff). An R with dsd <= -3 ms and dkpx > -0.5% -> H-radius, then an owner sheet
(side edge vs docs/owner_sheet_s7009_widewin_219.png, L4 far-left shoreline s7052). All R lose kpx >2% for the gain -> H-thin. dsd ~0 -> H-near.
