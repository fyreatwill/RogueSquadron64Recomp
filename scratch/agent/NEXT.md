# NEXT (s7237): score the WIDEWIN_R arms (soak s7235_widewin_r) or run them if the host is idle
HYPOTHESIS-ID: widewin-heavy-window-cost
State: knob ROGUESQ_DD_WIDEWIN_R=<cells> + _R_TOG=1 (s7233, default off). s7236 fixed its [s7233] tally (it never flushed: a fixed
128-placement threshold) to flush per phase every 2 s, and the scorer now prints CONTROL PASS/FAIL and exits 3 on FAIL or window not reached.
Build 19:33 2026-11-12 carries it. The arms are still unmeasured (owner active in s7233b, s7234, s7235 and s7236).
Hypotheses (s7232): H-radius (waste sits in far WW-only cells -> some R cuts sd >=3 ms with kpx loss <0.5%), H-thin (waste spread over all
WW distances -> no R helps without big kpx loss; need a coarser far mesh), H-near (cost does not move with R -> governor only).
Step 1: tail SOAK-RESULTS.md for s7235_widewin_r. rc=0: read the scorer output at the end of its soak_results log (also scratch/s7233b/).
rc=3: the control failed or the window was not reached. Read `grep -c '\[s7233\] ph=' scratch/s7233b/log_r*.txt`. 0 means the new
flush is still broken (placement call count: add a counter, check whether rs64_s7233_win runs at all in flight).
Still queued: check idle (`ioreg -c IOHIDSystem | awk '/HIDIdleTime/{print $NF/1e9; exit}'` >= 180) and lock. If idle, run
`zsh scratch/agent/soak_queue/s7235_widewin_r.sh` yourself (then move it to done/). If the owner is active, do NOT launch the game.
Positive control: CONTROL PASS on every arm (ph1 skip > 0, ph0 skip = 0). Read wide_by_d8 to see where the WW-only cells sit.
Outcome: per R, the window (t=77-97) dsd and dkpx (Ron - Roff). An R with dsd <= -3 ms and dkpx > -0.5% selects H-radius, then do an owner
sheet (side edge vs docs/owner_sheet_s7009_widewin_219.png, L4 far-left shoreline s7052). All R losing kpx >2% for the gain selects H-thin.
dsd ~0 selects H-near.
