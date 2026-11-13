# NEXT (s7239): score the WIDEWIN_R bracket arms (soak s7237_widewin_r2: R=48/64/72), then H-radius vs the 2x2 merge mesh
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7238): r40 window -3.19 ms / -8.6% kpx, r56 -1.94 ms loss-free; per-cell coarsening is impossible (retail level 2 = one quad per cell,
code-read buildGridCellMesh 0x8004B930 + 1.1-1.3 tri removed per skipped cell). Scorer prints `s7238 BAR MET|not met` per arm.
Step 1: tail SOAK-RESULTS.md for s7237_widewin_r2. rc=0: read the scorer block at the end of its soak_results log (data in scratch/s7237q/).
rc=2 or still queued: if `ioreg -c IOHIDSystem | awk '/HIDIdleTime/{print $NF/1e9; exit}'` >= 180, run
`zsh scratch/agent/soak_queue/s7237_widewin_r2.sh > scratch/s7237q/soak.log 2>&1` yourself, then move it to done/. A partial run still
scores any arm past t=97 (`python3 tools/s7233_widewin_r.py scratch/s7237q/log_r*.txt`).
Decide:
- H-radius: some R gives `s7238 BAR MET` (window dsd <= -2.5 ms, flight |dkpx| <= 1%). Owner sheet at that R (side edge vs
  docs/owner_sheet_s7009_widewin_219.png, L4 far-left shoreline s7052); offer it as an opt-in in OWNER-OPT-INS.
- No R meets the bar: build the 2x2 merge mesh past R (one quad spanning 2x2 WW-only cells: skip 3 of 4 cells, scale the kept cell's
  corner positions to the 2x2 extent and take the far corners' heights from the neighbours). Measure dsd, kpx and cracks (owner sheet).
- If the owner stays active all iteration: do the merge-mesh code-read offline (where 0x8004B644 gets x/z, how cell size enters) instead.
- Positive control: CONTROL PASS per arm.
