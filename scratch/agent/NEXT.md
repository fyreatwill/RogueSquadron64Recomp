# NEXT (s7238): score the WIDEWIN_R bracket arms (soak s7237_widewin_r2: R=48/64/72), then decide between H-radius and H-thin
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7237): r40 window dsd -3.19 ms / dkpx -8.6%, flight -1.61 / -3.3%; r56 window -1.94 / +3.8% (noise), flight -1.62 / +0.8%.
CONTROL PASS on both. The tog kpx noise floor is about +-4% in the window and +-1% in flight. H-near is refuted. Data are in scratch/s7233b/.
Step 1: tail SOAK-RESULTS.md for s7237_widewin_r2. rc=0 means: read the scorer block at the end of its soak_results log (data in scratch/s7237q/).
rc=2 (void) or still queued: if `ioreg -c IOHIDSystem | awk '/HIDIdleTime/{print $NF/1e9; exit}'` >= 180, run
`zsh scratch/agent/soak_queue/s7237_widewin_r2.sh > scratch/s7237q/soak.log 2>&1` yourself, then move it to done/. A partial run still
scores any arm past t=97 (`python3 tools/s7233_widewin_r.py scratch/s7237q/log_r*.txt`).
Decide:
- H-radius (softer bar): some R in 48-56 gives a window dsd <= -2.5 ms with a flight dkpx within +-1%. Make an owner sheet at that R
  (side edge vs docs/owner_sheet_s7009_widewin_219.png, L4 far-left shoreline s7052), and offer it as an opt-in in OWNER-OPT-INS.
- H-thin: dsd scales roughly linearly with kpx loss and no R beats about 1.7 ms loss-free. The next lever is a coarser far mesh for the WW-only
  cells (use the retail coarsest LOD slot for d8 >= R instead of skipping). This cuts zero-height tris, which are 40-50% of the cut.
- Positive control: CONTROL PASS per arm.
